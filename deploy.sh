#!/bin/bash

# Tallum Dutch Learning App Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p data logs/nginx ssl

# Set environment variables
if [ ! -f .env ]; then
    print_warning "No .env file found. Creating one with default values..."
    cat > .env << EOF
# Tallum App Environment Variables
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///data/words.db
FLASK_ENV=production
EOF
    print_status "Created .env file with generated SECRET_KEY"
else
    print_status "Using existing .env file"
fi

# Load environment variables
source .env

# Function to deploy
deploy() {
    local profile=$1
    
    print_status "Building Docker images..."
    docker-compose build
    
    print_status "Starting services with profile: $profile"
    if [ "$profile" = "production" ]; then
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml --profile production up -d
    else
        docker-compose up -d
    fi
    
    print_status "Waiting for services to start..."
    sleep 10
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        print_status "Services are running successfully!"
        print_status "Application is available at: http://localhost"
        print_status "API is available at: http://localhost/api/"
    else
        print_error "Some services failed to start. Check logs with: docker-compose logs"
        exit 1
    fi
}

# Function to stop services
stop() {
    print_status "Stopping services..."
    docker-compose down
    print_status "Services stopped"
}

# Function to view logs
logs() {
    print_status "Showing logs..."
    docker-compose logs -f
}

# Function to restart services
restart() {
    print_status "Restarting services..."
    docker-compose restart
    print_status "Services restarted"
}

# Function to update and redeploy
update() {
    print_status "Pulling latest changes..."
    git pull origin main
    
    print_status "Rebuilding and redeploying..."
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    
    print_status "Update completed!"
}

# Main script logic
case "${1:-deploy}" in
    "deploy")
        deploy "development"
        ;;
    "deploy-prod")
        deploy "production"
        ;;
    "stop")
        stop
        ;;
    "restart")
        restart
        ;;
    "logs")
        logs
        ;;
    "update")
        update
        ;;
    "help")
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  deploy       - Deploy the application (development mode)"
        echo "  deploy-prod  - Deploy the application (production mode with Nginx)"
        echo "  stop         - Stop all services"
        echo "  restart      - Restart all services"
        echo "  logs         - View logs"
        echo "  update       - Update and redeploy"
        echo "  help         - Show this help message"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac 