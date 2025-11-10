import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from urllib.parse import urljoin

def get_all_bike_models():
    """Get all bajaj bike model URLs from the main page"""
    
    url = "https://eauto.co.in/pages/online-spare-parts-price-list-by-bajaj-bike-model"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print("Fetching list of all bajaj bike models...")
    print("=" * 60)
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        bike_models = []
        
        # Strategy 1: Find all links in the page that contain /collections/
        all_links = soup.find_all('a', href=re.compile(r'/collections/.*bajaj', re.I))
        
        # Strategy 2: Also try finding links in specific sections
        if not all_links:
            all_links = soup.find_all('a', href=re.compile(r'/collections/'))
        
        for link in all_links:
            href = link.get('href')
            text = link.get_text(strip=True)
            
            if href and text:
                full_url = urljoin("https://eauto.co.in", href)
                
                # Avoid duplicates
                if not any(model['url'] == full_url for model in bike_models):
                    bike_models.append({
                        'name': text,
                        'url': full_url
                    })
        
        print(f"Found {len(bike_models)} bajaj bike models:")
        for i, model in enumerate(bike_models, 1):
            print(f"  {i}. {model['name']}")
        print("=" * 60)
        
        return bike_models
        
    except Exception as e:
        print(f"Error fetching bike models: {e}")
        return []


def scrape_products_from_url(url, model_name, headers):
    """Scrape all products from a specific bike model URL"""
    
    all_parts = []
    page = 1
    max_pages = 100
    
    print(f"\n{'*' * 60}")
    print(f"Scraping: {model_name}")
    print(f"{'*' * 60}")
    
    while page <= max_pages:
        if page == 1:
            page_url = url
        else:
            page_url = f"{url}?page={page}"
        
        print(f"  Page {page}...", end=" ")
        
        try:
            response = requests.get(page_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find products using multiple strategies
            products = []
            selectors = [
                ('div', {'class': 'grid__item'}),
                ('div', {'class': 'product-item'}),
                ('div', {'class': 'grid-product'}),
                ('li', {'class': 'grid__item'}),
                ('div', {'class': re.compile(r'product')}),
            ]
            
            for tag, attrs in selectors:
                products = soup.find_all(tag, attrs)
                if products:
                    break
            
            if not products:
                if page == 1:
                    print("No products found on first page")
                    # Debug: Print page structure
                    print("\n--- DEBUG: Analyzing page structure ---")
                    print("Looking for product containers...")
                    all_divs = soup.find_all('div', limit=20)
                    for div in all_divs:
                        classes = div.get('class', [])
                        if classes:
                            print(f"  Found div with classes: {classes}")
                    print("--- END DEBUG ---\n")
                else:
                    print("End of pages")
                break
            
            print(f"Found {len(products)} products", end=" ")
            
            # Extract product information
            products_extracted = 0
            for product in products:
                try:
                    # Extract name (multiple fallbacks)
                    name = None
                    name_selectors = [
                        ('div', {'class': 'grid-product__title'}),
                        ('a', {'class': 'grid-product__link'}),
                        ('h3', {}),
                        ('h2', {'class': 'h4'}),
                        ('div', {'class': 'product-title'}),
                    ]

                    for tag, attrs in name_selectors:
                        elem = product.find(tag, attrs)
                        if elem:
                            name = elem.get_text(strip=True)
                            if name:
                                break

                    # Fallbacks: link text/title, data-* attrs, image alt, aria-label, title attr
                    if not name:
                        link = product.find('a', href=re.compile(r'/products/'))
                        if link:
                            name = (link.get('title') or link.get_text(strip=True) or None)

                    if not name:
                        for attr in ('data-name', 'data-title', 'data-product-name', 'title', 'aria-label'):
                            val = product.get(attr)
                            if val:
                                name = val.strip()
                                break

                    if not name:
                        img = product.find('img', alt=True)
                        if img and img.get('alt'):
                            name = img.get('alt').strip()

                    # Extract price (multiple fallbacks)
                    price = None
                    price_selectors = [
                        ('span', {'class': re.compile(r'price.*current')}),
                        ('span', {'class': 'product-price__price'}),
                        ('div', {'class': 'price'}),
                        ('span', {'class': 'money'}),
                    ]

                    for tag, attrs in price_selectors:
                        elem = product.find(tag, attrs)
                        if elem:
                            price = elem.get_text(strip=True)
                            if price and ('₹' in price or 'Rs' in price or any(c.isdigit() for c in price)):
                                break

                    # Look for price-like attributes on the product or its children
                    if not price:
                        # Check attributes on the product container
                        for k, v in product.attrs.items():
                            if 'price' in k.lower() and v:
                                price = v if isinstance(v, str) else ' '.join(v) if isinstance(v, (list, tuple)) else str(v)
                                break

                    if not price:
                        # Check child elements for attributes containing price
                        for child in product.find_all(True):
                            for k, v in child.attrs.items():
                                if 'price' in k.lower() and v:
                                    price = v if isinstance(v, str) else ' '.join(v) if isinstance(v, (list, tuple)) else str(v)
                                    break
                            if price:
                                break

                    # itemprop="price" or meta tags inside product
                    if not price:
                        price_elem = product.find(attrs={'itemprop': 'price'})
                        if price_elem:
                            price = price_elem.get('content') or price_elem.get_text(strip=True)

                    # Fallback: regex search inside product text for currency/number
                    if not price:
                        text = product.get_text(' ', strip=True)
                        m = re.search(r'(?:₹|Rs\.?|INR)\s*[\d,]+\.?\d*', text)
                        if m:
                            price = m.group()
                        else:
                            # As a last resort, pick the first standalone number-looking token
                            m2 = re.search(r'[\d,]+(?:\.\d{1,2})?', text)
                            if m2:
                                price = m2.group()

                    # Clean price string to digits
                    if price:
                        price = price.replace('Sale price', '').replace('Regular price', '')
                        price = price.replace('Rs.', '').replace('₹', '').replace('\u00a0', ' ').strip()
                        price_match = re.search(r'[\d,]+\.?\d*', price)
                        if price_match:
                            price = price_match.group()
                    
                    # Extract URL
                    url_path = None
                    link_elem = product.find('a', href=re.compile(r'/products/'))
                    if link_elem and link_elem.get('href'):
                        url_path = urljoin("https://eauto.co.in", link_elem['href'])
                    
                    if name or url_path:
                        part_data = {
                            'Bike Brand': 'bajaj',
                            'Bike Model': model_name,
                            'Product Brand': 'bajaj',
                            'Product Name': name or "N/A",
                            'Price (₹)': price or "N/A",
                            'Product URL': url_path or "N/A"
                        }
                        all_parts.append(part_data)
                        products_extracted += 1
                    
                except Exception as e:
                    continue
            
            print(f"- Extracted {products_extracted} ✓")
            
            # Check for next page
            has_next = False
            pagination = soup.find(['nav', 'div', 'ul'], class_=re.compile(r'paginat', re.I))
            
            if pagination:
                next_link = pagination.find('a', string=re.compile(r'Next|›|»', re.I))
                if next_link and next_link.get('href'):
                    has_next = True
                
                if not has_next:
                    page_links = pagination.find_all('a', href=True)
                    for link in page_links:
                        try:
                            page_num = int(link.get_text(strip=True))
                            if page_num > page:
                                has_next = True
                                break
                        except (ValueError, AttributeError):
                            continue
            
            if not has_next:
                break
            
            page += 1
            time.sleep(1)
            
        except Exception as e:
            print(f"Error: {e}")
            break
    
    print(f"  Total products from {model_name}: {len(all_parts)}")
    return all_parts


def scrape_all_bajaj_bikes():
    """Main function to scrape all bajaj bike models"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # Get all bike models
    bike_models = get_all_bike_models()
    
    if not bike_models:
        print("Could not find any bike models. Please check the website.")
        return
    
    all_products = []
    
    # Scrape each bike model
    for i, model in enumerate(bike_models, 1):
        print(f"\n[{i}/{len(bike_models)}] Processing: {model['name']}")
        
        products = scrape_products_from_url(model['url'], model['name'], headers)
        all_products.extend(products)
        
        print(f"  Running total: {len(all_products)} products")
        
        # Add delay between models
        if i < len(bike_models):
            time.sleep(2)
    
    # Save to CSV
    if all_products:
        filename = 'bajaj_all_bikes_spare_parts.csv'
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['S.No', 'Bike Brand', 'Bike Model', 'Product Brand', 'Product Name', 'Price (₹)', 'Product URL']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for idx, part in enumerate(all_products, 1):
                part['S.No'] = idx
                writer.writerow(part)
        
        print("\n" + "=" * 60)
        print(f"✓ SCRAPING COMPLETE!")
        print(f"✓ Total bike models scraped: {len(bike_models)}")
        print(f"✓ Total products found: {len(all_products)}")
        print(f"✓ Data saved to: {filename}")
        print("=" * 60)
        
        # Show summary by model
        print("\nSummary by bike model:")
        model_counts = {}
        for product in all_products:
            model = product['Bike Model']
            model_counts[model] = model_counts.get(model, 0) + 1
        
        for model, count in sorted(model_counts.items()):
            print(f"  • {model}: {count} products")
        
        print(f"\n✓ You can now open '{filename}' in Excel or Google Sheets")
        
    else:
        print("\nNo products were scraped.")
    
    return all_products


if __name__ == "__main__":
    print("bajaj Bikes - Complete Spare Parts Scraper")
    print("=" * 60)
    products = scrape_all_bajaj_bikes()