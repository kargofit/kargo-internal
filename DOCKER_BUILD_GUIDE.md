# Docker Build Guide - Kargo Internal

This guide explains how to create and run the Docker image for the Kargo Internal application.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, but recommended)

### Check Docker Installation

```bash
# Check if Docker is installed
docker --version

# Check if Docker Compose is installed
docker-compose --version
```

## Method 1: Using Docker Compose (Recommended)

This is the easiest way to build and run the application.

### Step 1: Build and Start

```bash
# Navigate to the project directory
cd /Users/nk/Documents/kargo/data

# Build and start the container
docker-compose up -d
```

The `-d` flag runs the container in detached mode (in the background).

### Step 2: View Logs

```bash
# View logs
docker-compose logs -f

# View only recent logs
docker-compose logs --tail=50 -f
```

### Step 3: Stop the Container

```bash
# Stop the container
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Step 4: Rebuild After Changes

```bash
# Rebuild the image (if you made changes to the code)
docker-compose up -d --build

# Force rebuild without cache
docker-compose build --no-cache
docker-compose up -d
```

## Method 2: Using Docker Directly

### Step 1: Build the Docker Image

```bash
# Navigate to the project directory
cd /Users/nk/Documents/kargo/data

# Build the image
docker build -t kargo-internal .

# Build with a specific tag/version
docker build -t kargo-internal:1.0.0 .
```

### Step 2: Verify the Image

```bash
# List all images
docker images

# You should see kargo-internal in the list
```

### Step 3: Run the Container

```bash
# Run the container
docker run -d \
  --name kargo-internal \
  -p 5000:5000 \
  -v $(pwd)/temp:/app/temp \
  kargo-internal

# Or with environment variables
docker run -d \
  --name kargo-internal \
  -p 5000:5000 \
  -v $(pwd)/temp:/app/temp \
  -e ODOO_URL=https://kargo2.odoo.com \
  -e ODOO_DB=kargo2 \
  -e ODOO_USERNAME=admin@kargofit.com \
  -e ODOO_PASSWORD=your_password \
  kargo-internal
```

### Step 4: View Container Status

```bash
# Check if container is running
docker ps

# View container logs
docker logs -f kargo-internal

# View last 50 lines of logs
docker logs --tail=50 kargo-internal
```

### Step 5: Stop and Remove Container

```bash
# Stop the container
docker stop kargo-internal

# Remove the container
docker rm kargo-internal

# Stop and remove in one command
docker rm -f kargo-internal
```

## Accessing the Application

Once the container is running, access the application at:

```
http://localhost:5000
```

## Environment Variables

You can customize the application using environment variables:

### Using Docker Run

```bash
docker run -d \
  --name kargo-internal \
  -p 5000:5000 \
  -e ODOO_URL=https://kargo2.odoo.com \
  -e ODOO_DB=kargo2 \
  -e ODOO_USERNAME=admin@kargofit.com \
  -e ODOO_PASSWORD=your_password \
  -e FLASK_HOST=0.0.0.0 \
  -e FLASK_PORT=5000 \
  -e FLASK_DEBUG=false \
  kargo-internal
```

### Using Docker Compose

Edit the `docker-compose.yml` file:

```yaml
environment:
  - ODOO_URL=https://kargo2.odoo.com
  - ODOO_DB=kargo2
  - ODOO_USERNAME=admin@kargofit.com
  - ODOO_PASSWORD=your_password
  - FLASK_HOST=0.0.0.0
  - FLASK_PORT=5000
  - FLASK_DEBUG=false
```

Or use a `.env` file:

1. Create a `.env` file in the project directory:
```env
ODOO_URL=https://kargo2.odoo.com
ODOO_DB=kargo2
ODOO_USERNAME=admin@kargofit.com
ODOO_PASSWORD=your_password
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false
```

2. Update `docker-compose.yml` to use the `.env` file (it does this automatically)

3. Run:
```bash
docker-compose up -d
```

## Troubleshooting

### Container Won't Start

```bash
# Check container status
docker ps -a

# View error logs
docker logs kargo-internal

# Check if port 5000 is already in use
lsof -i :5000
# or
netstat -an | grep 5000
```

### Port Already in Use

If port 5000 is already in use, change the port mapping:

```bash
# In docker run, change -p 5000:5000 to -p 8080:5000
docker run -d --name kargo-internal -p 8080:5000 kargo-internal

# Then access at http://localhost:8080
```

Or in `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Changed from 5000:5000
```

### Rebuild After Code Changes

```bash
# Stop the container
docker-compose down

# Rebuild the image
docker-compose build --no-cache

# Start again
docker-compose up -d
```

### View Container Health

```bash
# Check health status
docker ps

# Inspect container
docker inspect kargo-internal

# Check health check logs
docker inspect --format='{{json .State.Health}}' kargo-internal | jq
```

### Remove All Containers and Images

```bash
# Stop all containers
docker stop $(docker ps -aq)

# Remove all containers
docker rm $(docker ps -aq)

# Remove the image
docker rmi kargo-internal

# Remove all unused images
docker image prune -a
```

## Quick Reference Commands

```bash
# Build image
docker build -t kargo-internal .

# Run container
docker run -d --name kargo-internal -p 5000:5000 kargo-internal

# View logs
docker logs -f kargo-internal

# Stop container
docker stop kargo-internal

# Start container
docker start kargo-internal

# Restart container
docker restart kargo-internal

# Remove container
docker rm kargo-internal

# Using Docker Compose
docker-compose up -d          # Start
docker-compose down           # Stop
docker-compose logs -f        # View logs
docker-compose restart        # Restart
docker-compose ps             # Check status
```

## Production Deployment

For production, consider:

1. **Use a production WSGI server** (like Gunicorn)
2. **Set up reverse proxy** (like Nginx)
3. **Use Docker secrets** for sensitive data
4. **Enable HTTPS/SSL**
5. **Set up monitoring and logging**
6. **Use a container orchestration platform** (like Kubernetes)

### Example with Gunicorn

Update the Dockerfile to use Gunicorn:

```dockerfile
# Install Gunicorn
RUN pip install --no-cache-dir gunicorn

# Change CMD to use Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/latest/deploying/)

