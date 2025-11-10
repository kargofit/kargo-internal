import xmlrpc.client
import ssl
import re
from html import unescape

# Odoo connection details
ODOO_URL = URL = "https://kargo2.odoo.com"  # e.g., https://kargofit.odoo.com
ODOO_DB = DB = "kargo2"  # e.g., kargofit
ODOO_USERNAME = USERNAME = "admin@kargofit.com"
ODOO_PASSWORD = PASSWORD = "af74742249c06aa4aee821b557c33f0d54267971"
# City filter (change as needed)
CITY_FILTER = 'Patna'  # Replace with desired city
SALES_REP = ['Manas', 'Satyam']

def connect_odoo():
    """Establish connection to Odoo and authenticate"""
    try:
        # Create SSL context (for HTTPS connections)
        context = ssl._create_unverified_context()
        
        # Connect to authentication endpoint
        common = xmlrpc.client.ServerProxy(
            f'{ODOO_URL}/xmlrpc/2/common',
            context=context
        )
        
        # Authenticate and get user ID
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        
        if not uid:
            print("Authentication failed! Check credentials.")
            return None, None
        
        print(f"Successfully authenticated. User ID: {uid}")
        
        # Connect to object endpoint
        models = xmlrpc.client.ServerProxy(
            f'{ODOO_URL}/xmlrpc/2/object',
            context=context
        )
        
        return uid, models
    
    except Exception as e:
        print(f"Connection error: {e}")
        return None, None

def clean_html(html_text):
    """Remove HTML tags and convert to plain text"""
    if not html_text:
        return 'N/A'
    
    # Convert HTML entities to characters (e.g., &nbsp; to space)
    text = unescape(str(html_text))
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text if text else 'N/A'

def fetch_customers_by_city(uid, models, city, sales_rep):
    """Fetch customers filtered by city"""
    try:
        # Define search domain (filter criteria)
        domain = [
            # ('customer_rank', '>', 0),  # Only customers (not suppliers)
            ('city', '=', city),  # City filter
            ('x_studio_sales_rep', '=', sales_rep)  # Sales representative filter (if needed)
        ]
        
        # Define fields to fetch
        fields = [
            'name',          # Customer name
            'street',        # Street address
            'phone',         # Phone number
            'x_studio_sales_rep',  # Custom field: Sales representative
            'comment'        # Notes/Internal notes
        ]
        
        # Search and read records
        customers = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'search_read',
            [domain],
            {'fields': fields}
        )
        
        # Clean HTML from comment field
        for customer in customers:
            if 'comment' in customer:
                customer['comment'] = clean_html(customer['comment'])
        
        return customers
    
    except Exception as e:
        print(f"Error fetching customers: {e}")
        return []

def display_customers(customers):
    """Display customer information"""
    if not customers:
        print(f"No customers found with the specified filter.")
        return
    
    print(f"\n{'='*80}")
    print(f"Found {len(customers)} customer(s)")
    print(f"{'='*80}\n")
    
    for idx, customer in enumerate(customers, 1):
        print(f"Customer #{idx}")
        print(f"  ID: {customer.get('id', 'N/A')}")
        print(f"  Name: {customer.get('name', 'N/A')}")
        print(f"  Street: {customer.get('street', 'N/A')}")
        print(f"  Phone: {customer.get('phone', 'N/A')}")
        print(f"  Notes: {customer.get('comment', 'N/A')}")
        print(f"{'-'*80}\n")

def main():
    """Main execution function"""
    print("Connecting to Odoo...")
    
    # Connect and authenticate
    uid, models = connect_odoo()
    
    if not uid or not models:
        print("Failed to connect to Odoo. Exiting.")
        return
    
    # Fetch customers
    print(f"\nFetching customers from city: {CITY_FILTER}...")
    for sales_rep in SALES_REP:
        customers = fetch_customers_by_city(uid, models, CITY_FILTER, sales_rep)
        save_to_csv(customers, sales_rep)

def save_to_csv(customers, name):
    """Save customer data to CSV file"""
    import csv
    from datetime import datetime
    
    if not customers:
        print("No data to export.")
        return
    
    filename = f"{name}_customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'name', 'street', 'phone', 'comment', 'x_studio_sales_rep'])
            writer.writeheader()
            writer.writerows(customers)
        
        print(f"Data exported successfully to {filename}")
    
    except Exception as e:
        print(f"Error exporting to CSV: {e}")

if __name__ == "__main__":
    main()