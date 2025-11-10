import csv
import sys
import re
from html import unescape
from pathlib import Path


def strip_html_keep_text(value: str) -> str:
    if value is None:
        return ""
    text = str(value)
    # Normalize common line-break tags to newlines before stripping
    text = re.sub(r"<\s*br\s*/?\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<\s*/?\s*p\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<\s*li\s*>", "- ", text, flags=re.IGNORECASE)
    text = re.sub(r"<\s*/\s*li\s*>", "\n", text, flags=re.IGNORECASE)

    # Remove all remaining tags
    text = re.sub(r"<[^>]+>", "", text, flags=re.DOTALL)

    # Decode HTML entities
    text = unescape(text)

    # Collapse excessive whitespace, preserve newlines (convert multiple newlines to single)
    # First, replace Windows newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse spaces and tabs around newlines
    text = re.sub(r"[\t\f\v ]+", " ", text)
    text = re.sub(r"\s*\n\s*", "\n", text)
    # Trim lines and overall text
    text = "\n".join(line.strip() for line in text.split("\n")).strip()
    return text


def clean_csv(input_path: Path, output_path: Path) -> None:
    with input_path.open("r", newline="", encoding="utf-8") as infile:
        # Sniff dialect for safer read
        sample = infile.read(4096)
        infile.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample)
        except csv.Error:
            dialect = csv.excel

        reader = csv.DictReader(infile, dialect=dialect)
        fieldnames = reader.fieldnames or []
        # If sniffer mis-detected delimiter (single header containing commas), force excel (comma)
        if len(fieldnames) == 1 and "," in fieldnames[0]:
            infile.seek(0)
            dialect = csv.excel
            reader = csv.DictReader(infile, dialect=dialect)
            fieldnames = reader.fieldnames or []
        if not fieldnames:
            raise SystemExit("CSV appears to have no header row.")

        # Find Notes column robustly
        def normalize(h: str) -> str:
            h = (h or "").lstrip("\ufeff").strip().lower()
            # drop non-alphanumeric to tolerate odd separators/spaces
            return "".join(ch for ch in h if ch.isalnum())

        notes_key = None
        # Exact preferred
        for name in fieldnames:
            if name == "Notes":
                notes_key = name
                break
        # Case-insensitive/trimmed
        if notes_key is None:
            for name in fieldnames:
                if name and name.strip().lower() == "notes":
                    notes_key = name
                    break
        # Alphanumeric-only match
        if notes_key is None:
            for name in fieldnames:
                if normalize(name) == "notes":
                    notes_key = name
                    break
        if notes_key is None:
            # Fallback: assume last column is Notes
            notes_key = fieldnames[-1]
            print(
                f"Warning: 'Notes' column not matched; falling back to last column: '{notes_key}'",
                file=sys.stderr,
            )

        with output_path.open("w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames, dialect=dialect)
            writer.writeheader()
            for row in reader:
                value = row.get(notes_key, "")
                row[notes_key] = strip_html_keep_text(value)
                writer.writerow(row)


def main(argv: list[str]) -> int:
    if len(argv) >= 2:
        input_file = Path(argv[1])
    else:
        input_file = Path("Contact with notes.csv")

    if len(argv) >= 3:
        output_file = Path(argv[2])
    else:
        output_file = input_file.with_name(input_file.stem + ".cleaned.csv")

    if not input_file.exists():
        print(f"Input file not found: {input_file}", file=sys.stderr)
        return 1

    clean_csv(input_file, output_file)
    print(f"Wrote cleaned CSV: {output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))


