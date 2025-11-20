import xmlrpc.client
import ssl
import re
import csv
import io
from html import unescape
from flask import Flask, render_template, send_file, jsonify, request
from datetime import datetime
import os
from whatsapp_service import WhatsAppService

app = Flask(__name__)

# Odoo connection details (can be overridden by environment variables)
ODOO_URL = os.getenv('ODOO_URL', 'https://kargo3.odoo.com')
ODOO_DB = os.getenv('ODOO_DB', 'kargo3')
ODOO_USERNAME = os.getenv('ODOO_USERNAME', 'admin@kargofit.com')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'af74742249c06aa4aee821b557c33f0d54267971')

# Flask configuration
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

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
            return None, None
        
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
        return ''
    
    # Convert HTML entities to characters (e.g., &nbsp; to space)
    text = unescape(str(html_text))
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Normalize line breaks
    text = re.sub(r'<\s*br\s*/?\s*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<\s*/?\s*p\s*>', '\n', text, flags=re.IGNORECASE)
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s*\n\s*', '\n', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text if text else ''

def fetch_customers(uid, models, city=None, sales_rep=None, limit=1000):
    """Fetch customers from Odoo with optional filters"""
    try:
        # Define search domain (filter criteria)
        domain = []
        
        if city:
            domain.append(('city', '=', city))
        if sales_rep:
            domain.append(('x_studio_sales_rep', '=', sales_rep))
        
        # Define fields to fetch
        fields = [
            'id',            
            'name',          # Customer name
            'street',        # Street address
            'phone',         # Phone number
            'city',          # City
            'x_studio_follow_up_date',
            'x_studio_sales_rep',  # Custom field: Sales representative
            'comment'        # Notes/Internal notes
        ]
        
        # Search and read records
        customers = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'search_read',
            [domain],
            {'fields': fields, 'limit': limit}
        )
        
        # Clean HTML from comment field and handle tuple fields
        for customer in customers:
            if 'comment' in customer:
                customer['comment'] = clean_html(customer['comment'])
            # Handle tuple fields (like Many2one fields - format: (id, name))
            for key in customer:
                if key == 'id':
                    continue
                if isinstance(customer[key], tuple):
                    # Many2one fields are tuples: (id, display_name)
                    customer[key] = customer[key][1] if len(customer[key]) > 1 else str(customer[key][0])
                elif customer[key] is None:
                    customer[key] = ''
                elif isinstance(customer[key], bool):
                    customer[key] = 'True' if customer[key] else 'False'
                elif not isinstance(customer[key], str):
                    customer[key] = str(customer[key])
        
        return customers
    
    except Exception as e:
        print(f"Error fetching customers: {e}")
        return []

def fetch_sales_stats(uid, models, partner_ids, states=None):
    try:
        if not partner_ids:
            return {}
        states = states or ['sale', 'done']
        domain = [('partner_id', 'in', partner_ids)]
        if states:
            domain.append(('state', 'in', states))
        groups = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order', 'read_group',
            [domain],
            {
                'fields': ['amount_total:sum'],
                'groupby': ['partner_id'],
                'lazy': False
            }
        )
        stats = {}
        for g in groups:
            pid = None
            v = g.get('partner_id')
            if isinstance(v, (list, tuple)) and v:
                pid = v[0]
            elif isinstance(v, int):
                pid = v
            elif isinstance(v, str) and v.isdigit():
                pid = int(v)
            cnt = g.get('__count')
            if cnt is None:
                cnt = g.get('partner_id_count', 0)
            amt = g.get('amount_total')
            if amt is None:
                amt = g.get('amount_total_sum', 0.0)
            if pid is not None:
                stats[pid] = {
                    'sale_order_count': int(cnt or 0),
                    'sale_order_amount_total': float(amt or 0.0)
                }
        return stats
    except Exception as e:
        print(f"Error fetching sales stats: {e}")
        return {}

def generate_csv(customers):
    """Generate CSV content from customer data"""
    if not customers:
        return None
    
    # Create in-memory file
    output = io.StringIO()
    
    # Define field names
    fieldnames = [
            'name',          # Customer name
            'street',        # Street address
            'phone',         # Phone number
            'x_studio_follow_up_date',
            'x_studio_sales_rep',  # Custom field: Sales representative
            'comment',        # Notes/Internal notes
            'sale_order_count',
            'sale_order_amount_total'
        ]
        
    # Create CSV writer
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    
    # Write customer data
    for customer in customers:
        # Flatten the data
        row = {}
        for field in fieldnames:
            value = customer.get(field, '')
            # Handle tuple fields
            if isinstance(value, tuple):
                value = value[1] if len(value) > 1 else value[0]
            row[field] = value if value else ''
        writer.writerow(row)
    
    # Get CSV content
    csv_content = output.getvalue()
    output.close()
    
    return csv_content

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/customers')
def customers():
    """Render the customers list page"""
    return render_template('customers.html')

@app.route('/api/generate-csv', methods=['POST'])
def generate_csv_endpoint():
    """Generate CSV from Odoo data"""
    try:
        # Get filters from request
        data = request.get_json() or {}
        city = data.get('city')
        sales_rep = data.get('sales_rep')
        
        # Convert empty strings to None
        city = city if city else None
        sales_rep = sales_rep if sales_rep else None
        
        # Connect to Odoo
        uid, models = connect_odoo()
        
        if not uid or not models:
            return jsonify({'error': 'Failed to connect to Odoo. Please check credentials.'}), 500
        
        # Fetch customers
        customers = fetch_customers(uid, models, city=city, sales_rep=sales_rep)

        partner_ids = [c.get('id') for c in customers if isinstance(c.get('id'), int)]
        stats = fetch_sales_stats(uid, models, partner_ids)
        for c in customers:
            sid = c.get('id') if isinstance(c.get('id'), int) else None
            s = stats.get(sid, {})
            c['sale_order_count'] = s.get('sale_order_count', 0)
            c['sale_order_amount_total'] = s.get('sale_order_amount_total', 0.0)
        
        if not customers:
            filter_msg = []
            if city:
                filter_msg.append(f"city: {city}")
            if sales_rep:
                filter_msg.append(f"sales rep: {sales_rep}")
            filter_text = f" with filters ({', '.join(filter_msg)})" if filter_msg else ""
            return jsonify({'error': f'No customers found{filter_text}.'}), 404
        
        # Generate CSV
        csv_content = generate_csv(customers)
        
        if not csv_content:
            return jsonify({'error': 'Failed to generate CSV.'}), 500
        
        # Create filename with timestamp and filters
        filter_parts = []
        if city:
            filter_parts.append(city.lower().replace(' ', '_'))
        if sales_rep:
            filter_parts.append(sales_rep.lower().replace(' ', '_'))
        filter_suffix = '_' + '_'.join(filter_parts) if filter_parts else ''
        filename = f"kargo_export{filter_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Save to temporary file
        temp_dir = 'temp'
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, filename)
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'count': len(customers),
            'download_url': f'/download/{filename}'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download the generated CSV file"""
    try:
        temp_path = os.path.join('temp', filename)
        
        if not os.path.exists(temp_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers', methods=['GET'])
def get_customers():
    """Get customers from Odoo with filters"""
    try:
        # Get filters from query parameters
        city = request.args.get('city', '').strip() or None
        sales_rep = request.args.get('sales_rep', '').strip() or None
        limit = int(request.args.get('limit', 1000))
        
        # Connect to Odoo
        uid, models = connect_odoo()
        
        if not uid or not models:
            return jsonify({'error': 'Failed to connect to Odoo. Please check credentials.'}), 500
        
        # Fetch customers
        customers = fetch_customers(uid, models, city=city, sales_rep=sales_rep, limit=limit)
        partner_ids = [c.get('id') for c in customers if isinstance(c.get('id'), int)]
        stats = fetch_sales_stats(uid, models, partner_ids)
        for c in customers:
            sid = c.get('id') if isinstance(c.get('id'), int) else None
            s = stats.get(sid, {})
            c['sale_order_count'] = s.get('sale_order_count', 0)
            c['sale_order_amount_total'] = s.get('sale_order_amount_total', 0.0)
        
        # Prepare phone numbers for each customer
        for customer in customers:
            # Use phone field only (mobile field is ignored)
            phone = customer.get('phone') or ''
            # Clean phone number - remove spaces, dashes, parentheses, plus signs
            phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')
            
            # Handle Indian phone numbers
            if phone:
                # If starts with 0, remove it
                if phone.startswith('0'):
                    phone = phone[1:]
                # If 10 digits and doesn't start with country code, add 91 (India)
                if len(phone) == 10 and not phone.startswith('91'):
                    phone = '91' + phone
                # If starts with 91 and has 12 digits, it's valid
                # If has 10+ digits, it's potentially valid
            
            customer['phone_number'] = phone
            customer['has_phone'] = bool(phone and len(phone) >= 10)
        
        return jsonify({
            'success': True,
            'customers': customers,
            'count': len(customers),
            'filters': {
                'city': city,
                'sales_rep': sales_rep
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/send-whatsapp', methods=['POST'])
def send_whatsapp():
    """Send WhatsApp messages to selected customers"""
    try:
        data = request.get_json() or {}
        phone_numbers = data.get('phone_numbers', [])
        message = data.get('message', '')
        
        if not phone_numbers:
            return jsonify({'error': 'No phone numbers provided'}), 400
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Initialize WhatsApp service
        whatsapp = WhatsAppService()
        
        # Send bulk messages
        results = whatsapp.send_bulk_messages(phone_numbers, message)
        
        return jsonify({
            'success': True,
            'results': results
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-connection', methods=['GET'])
def test_connection():
    """Test Odoo connection"""
    try:
        uid, models = connect_odoo()
        
        if not uid or not models:
            return jsonify({'success': False, 'message': 'Failed to connect to Odoo'}), 500
        
        return jsonify({'success': True, 'message': 'Successfully connected to Odoo', 'uid': uid})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    # Create temp directory if it doesn't exist
    os.makedirs('temp', exist_ok=True)
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT)
