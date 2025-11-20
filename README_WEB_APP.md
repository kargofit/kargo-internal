# Kargo Internal - Customer Data Export

A modern web application to generate and download CSV files from Odoo customer/partner data.

## Features

- 🎨 Modern, clean, and responsive UI
- 📊 Generate CSV from Odoo contacts/partners
- 🔍 Filter by city (default: Patna) and sales representative
- 📥 Download generated CSV files
- 🚀 Easy to use interface
- 📱 Fully mobile-friendly

## Requirements

- Python 3.12+
- Flask (already installed in venv)
- Odoo credentials configured in `app.py`

## How to Run

1. Activate the virtual environment:
```bash
source venv/bin/activate
```

2. Run the Flask application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

1. **Select City**: Choose a city from the dropdown (default: Patna) or select "All Cities"
2. **Select Sales Representative**: Choose a sales rep from the dropdown (Manas, Satyam, Ankit) or select "All Representatives"
3. **Generate CSV**: Click the "Generate CSV Export" button to fetch data from Odoo and generate the CSV
4. **Download**: Once generated, click the "Download CSV" button to download the file

## Configuration

Edit the following variables in `app.py` to match your Odoo instance:

```python
ODOO_URL = "https://kargo3.odoo.com"
ODOO_DB = "kargo3"
ODOO_USERNAME = "admin@kargofit.com"
ODOO_PASSWORD = "af74742249c06aa4aee821b557c33f0d54267971"
```

## CSV Fields

The generated CSV includes the following fields:
- name (Customer name)
- street (Street address)
- phone (Phone number)
- x_studio_sales_rep (Sales Representative)
- comment (Notes - HTML cleaned)

## Notes

- Generated CSV files are temporarily stored in the `temp/` directory
- HTML tags are automatically removed from the notes/comments field
- The app handles connection errors gracefully
- Files are named with timestamps for easy identification

## Troubleshooting

- **Connection Failed**: Check your Odoo credentials and network connection
- **No Data Found**: Verify your filters (city, sales rep) are correct
- **Download Not Working**: Ensure the `temp/` directory exists and has write permissions

