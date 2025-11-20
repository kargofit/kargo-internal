# Docker Setup for Odoo CSV Generator

This guide explains how to run the Odoo CSV Generator web application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, for easier management)

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Build and run the container:**
   ```bash
   docker-compose up -d
   ```

2. **View logs:**
   ```bash
   docker-compose logs -f
   ```

3. **Stop the container:**
   ```bash
   docker-compose down
   ```

### Option 2: Using Docker directly

1. **Build the Docker image:**
   ```bash
   docker build -t odoo-csv-generator .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     -p 5000:5000 \
     -e ODOO_URL=https://kargo3.odoo.com \
     -e ODOO_DB=kargo3 \
     -e ODOO_USERNAME=admin@kargofit.com \
     -e ODOO_PASSWORD=your_password \
     --name odoo-csv-generator \
     odoo-csv-generator
   ```

3. **View logs:**
   ```bash
   docker logs -f odoo-csv-generator
   ```

4. **Stop the container:**
   ```bash
   docker stop odoo-csv-generator
   ```

## Environment Variables

You can customize the application using environment variables:

- `ODOO_URL`: Odoo server URL (default: `https://kargo3.odoo.com`)
- `ODOO_DB`: Database name (default: `kargo3`)
- `ODOO_USERNAME`: Odoo username (default: `admin@kargofit.com`)
- `ODOO_PASSWORD`: Odoo password/API key
- `FLASK_HOST`: Host to bind to (default: `0.0.0.0`)
- `FLASK_PORT`: Port to bind to (default: `5000`)
- `FLASK_DEBUG`: Enable debug mode (default: `false`)

## Accessing the Application

Once the container is running, access the web application at:
```
http://localhost:5000
```

## Persisting Data

The `temp/` directory is mounted as a volume in docker-compose.yml, so generated CSV files will persist on your host machine.

## Health Check

The container includes a health check that monitors the application's status. You can check the health status with:

```bash
docker ps
```

Look for the "STATUS" column to see if the container is healthy.

## Troubleshooting

### Container won't start
- Check if port 5000 is already in use: `lsof -i :5000`
- View container logs: `docker logs odoo-csv-generator`

### Connection issues
- Verify Odoo credentials are correct
- Check network connectivity to Odoo server
- Test connection using the "Test Connection" button in the web UI

### CSV files not downloading
- Ensure the `temp/` directory has write permissions
- Check container logs for errors
- Verify the volume is mounted correctly (if using docker-compose)

## Building for Production

For production deployments:

1. Set `FLASK_DEBUG=false` in environment variables
2. Use a production WSGI server like gunicorn
3. Configure proper SSL/TLS
4. Set up proper logging
5. Use secrets management for credentials

## Updating the Application

To update the application:

1. **Stop the container:**
   ```bash
   docker-compose down
   ```

2. **Rebuild the image:**
   ```bash
   docker-compose build --no-cache
   ```

3. **Start the container:**
   ```bash
   docker-compose up -d
   ```

## Security Notes

- Never commit credentials to version control
- Use environment variables or secrets management for sensitive data
- Regularly update Docker images for security patches
- Consider using Docker secrets for production deployments

