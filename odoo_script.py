import xmlrpc.client
# Odoo connection details
URL = "https://kargofit.odoo.com"  # e.g., https://kargofit.odoo.com
DB = "kargofit"  # e.g., kargofit
USERNAME = "admin@kargofit.com"
PASSWORD = "af74742249c06aa4aee821b557c33f0d54267971"

# Authenticate
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})

# Connect to the object endpoint
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")


class OdooProductManager:
    def __init__(self, url, db, username, password):
        """
        Initialize Odoo connection
        
        Args:
            url: Odoo server URL (e.g., 'http://localhost:8069')
            db: Database name
            username: Odoo username
            password: Odoo password or API key
        """
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        
        # Authenticate
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.uid = common.authenticate(db, username, password, {})
        
        # Models proxy
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
    def create_custom_fields(self):
        """
        Create custom fields for brand, volume, and unit if they don't exist
        Note: This requires admin privileges and the field creation might need
        to be done through the Odoo UI or a module
        """
        # Custom fields are typically created through Odoo modules
        # This is a placeholder to show the structure
        print("Custom fields should be created through Odoo Studio or a custom module")
        print("Required fields: x_brand, x_volume, x_unit")
        
    def create_product(self, name, brand, volume, unit, **kwargs):
        """
        Create a product with custom properties
        
        Args:
            name: Product name
            brand: Brand name
            volume: Volume quantity
            unit: Unit of measurement (e.g., 'ml', 'L', 'kg', 'g')
            **kwargs: Additional product fields (price, description, etc.)
        
        Returns:
            Product ID if successful, None otherwise
        """
        try:
            # Prepare product values
            product_vals = {
                'name': name,
                'type': kwargs.get('type', 'consu'),  # consu, service, or product
                'list_price': kwargs.get('list_price', 0.0),
                'standard_price': kwargs.get('standard_price', 0.0),
                'description': kwargs.get('description', ''),
                'default_code': kwargs.get('default_code', ''),  # Internal reference
                'barcode': kwargs.get('barcode', ''),
                # Custom fields (prefix with x_ for custom fields)
                'x_brand': brand,
                'x_volume': volume,
                'x_unit': unit,
            }
            
            # Create product
            product_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                'product.product', 'create',
                [product_vals]
            )
            
            print(f"Product created successfully with ID: {product_id}")
            return product_id
            
        except Exception as e:
            print(f"Error creating product: {e}")
            return None
    
    def create_product_template(self, name, brand, volume, unit, **kwargs):
        """
        Create a product template (product.template) with custom properties
        Use this for products with variants
        
        Args:
            name: Product template name
            brand: Brand name
            volume: Volume quantity
            unit: Unit of measurement
            **kwargs: Additional fields
        
        Returns:
            Product template ID if successful, None otherwise
        """
        try:
            template_vals = {
                'name': name,
                'type': kwargs.get('type', 'consu'),
                'list_price': kwargs.get('list_price', 0.0),
                'standard_price': kwargs.get('standard_price', 0.0),
                'description': kwargs.get('description', ''),
                'default_code': kwargs.get('default_code', ''),
                'barcode': kwargs.get('barcode', ''),
                'x_brand': brand,
                'x_volume': volume,
                'x_unit': unit,
            }
            
            template_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                'product.template', 'create',
                [template_vals]
            )
            
            print(f"Product template created successfully with ID: {template_id}")
            return template_id
            
        except Exception as e:
            print(f"Error creating product template: {e}")
            return None
    
    def search_products(self, filters):
        """
        Search for products based on filters
        
        Args:
            filters: List of filter tuples, e.g., [('x_brand', '=', 'Nike')]
        
        Returns:
            List of product IDs
        """
        try:
            product_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'product.product', 'search',
                [filters]
            )
            return product_ids
        except Exception as e:
            print(f"Error searching products: {e}")
            return []
    
    def read_products(self, product_ids, fields=None):
        """
        Read product data
        
        Args:
            product_ids: List of product IDs
            fields: List of fields to retrieve (None for all)
        
        Returns:
            List of product dictionaries
        """
        try:
            if fields is None:
                fields = ['name', 'x_brand', 'x_volume', 'x_unit', 'list_price']
            
            products = self.models.execute_kw(
                self.db, self.uid, self.password,
                'product.product', 'read',
                [product_ids, fields]
            )
            return products
        except Exception as e:
            print(f"Error reading products: {e}")
            return []


# Example usage
if __name__ == "__main__":
    # Initialize manager
    manager = OdooProductManager(URL, DB, USERNAME, PASSWORD)
    
    # Create a single product
    product_id = manager.create_product(
        name="Coca Cola Regular",
        brand="Coca Cola",
        volume=500,
        unit="ml",
        list_price=2.50,
        standard_price=1.50,
        default_code="COKE-500ML",
        barcode="1234567890123",
        description="Refreshing cola drink"
    )
    
    # Create multiple products
    products_to_create = [
        {
            "name": "Pepsi Regular",
            "brand": "Pepsi",
            "volume": 500,
            "unit": "ml",
            "list_price": 2.45,
            "standard_price": 1.45
        },
        {
            "name": "Sprite Lemon",
            "brand": "Sprite",
            "volume": 330,
            "unit": "ml",
            "list_price": 2.00,
            "standard_price": 1.20
        },
        {
            "name": "Mountain Dew",
            "brand": "Mountain Dew",
            "volume": 1,
            "unit": "L",
            "list_price": 3.50,
            "standard_price": 2.00
        }
    ]
    
    for product_data in products_to_create:
        manager.create_product(**product_data)
    
    # Search for products by brand
    coca_cola_products = manager.search_products([('x_brand', '=', 'Coca Cola')])
    print(f"\nCoca Cola products found: {coca_cola_products}")
    
    # Read product details
    if coca_cola_products:
        product_details = manager.read_products(coca_cola_products)
        print("\nProduct details:")
        for product in product_details:
            print(f"  - {product['name']}: {product['x_volume']}{product['x_unit']} - ${product['list_price']}")