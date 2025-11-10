# Quick Start Guide - Kargo Internal

## Mobile-Friendly Customer Data Export App

### 🚀 Running with Docker Compose (Easiest)

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Access at: http://localhost:5000

### 🐳 Running with Docker

```bash
# Build image
docker build -t odoo-csv-generator .

# Run container
docker run -d -p 5000:5000 --name odoo-csv-generator odoo-csv-generator

# View logs
docker logs -f odoo-csv-generator

# Stop
docker stop odoo-csv-generator
```

### 💻 Running Locally (Without Docker)

```bash
# Activate virtual environment
source venv/bin/activate

# Run application
python app.py
```

Access at: http://localhost:5000

### 📱 Mobile Features

- ✅ Fully responsive design
- ✅ Touch-friendly buttons (minimum 44px touch targets)
- ✅ Optimized for mobile browsers
- ✅ Prevents iOS zoom on input focus
- ✅ Mobile-optimized layout and spacing
- ✅ Works on all screen sizes

### 🔧 Environment Variables

Set these in `docker-compose.yml` or as environment variables:

- `ODOO_URL` - Odoo server URL
- `ODOO_DB` - Database name
- `ODOO_USERNAME` - Odoo username
- `ODOO_PASSWORD` - Odoo password/API key
- `FLASK_HOST` - Host (default: 0.0.0.0)
- `FLASK_PORT` - Port (default: 5000)
- `FLASK_DEBUG` - Debug mode (default: false)

### 📋 Features

- Generate CSV from Odoo contacts
- Filter by city (default: Patna) and sales representative (Manas, Satyam, Ankit)
- Download generated CSV files
- Modern, clean UI design
- Mobile-friendly interface
- Real-time status updates
- Smart filename generation with filters

