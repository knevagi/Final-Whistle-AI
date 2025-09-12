#!/bin/bash
# Deployment script for Final Whistle AI

set -e

echo "🚀 Starting Final Whistle AI Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    print_status "All dependencies are installed"
}

# Setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    # Copy environment template if .env doesn't exist
    if [ ! -f .env ]; then
        if [ -f env.production.template ]; then
            cp env.production.template .env
            print_warning "Created .env from template. Please update with your actual values."
        else
            print_error ".env file not found and no template available"
            exit 1
        fi
    fi
    
    print_status "Environment setup complete"
}

# Install frontend dependencies
install_frontend() {
    print_status "Installing frontend dependencies..."
    npm install
    print_status "Frontend dependencies installed"
}

# Build frontend
build_frontend() {
    print_status "Building frontend..."
    npm run build
    print_status "Frontend build complete"
}

# Install backend dependencies
install_backend() {
    print_status "Installing backend dependencies..."
    
    # Install API dependencies
    cd api
    pip install -r requirements.txt
    cd ..
    
    # Install Crew AI dependencies
    cd crew_ai
    pip install -r requirements.txt
    cd ..
    
    # Install Fixture Service dependencies
    cd crew_ai/fixture_service
    pip install -r requirements.txt
    cd ../..
    
    print_status "Backend dependencies installed"
}

# Test the application
test_application() {
    print_status "Testing application..."
    
    # Test API
    cd api
    python test_api.py
    cd ..
    
    print_status "Application tests passed"
}

# Deploy based on method
deploy() {
    local method=$1
    
    case $method in
        "vercel")
            deploy_vercel
            ;;
        "docker")
            deploy_docker
            ;;
        "railway")
            deploy_railway
            ;;
        *)
            print_error "Unknown deployment method: $method"
            print_error "Available methods: vercel, docker, railway"
            exit 1
            ;;
    esac
}

# Deploy to Vercel
deploy_vercel() {
    print_status "Deploying to Vercel..."
    
    if ! command -v vercel &> /dev/null; then
        print_error "Vercel CLI is not installed. Install with: npm install -g vercel"
        exit 1
    fi
    
    vercel --prod
    print_status "Deployed to Vercel"
}

# Deploy with Docker
deploy_docker() {
    print_status "Deploying with Docker..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    docker-compose up --build -d
    print_status "Deployed with Docker"
}

# Deploy to Railway
deploy_railway() {
    print_status "Deploying to Railway..."
    
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI is not installed. Install with: npm install -g @railway/cli"
        exit 1
    fi
    
    railway login
    railway init
    railway up
    print_status "Deployed to Railway"
}

# Main deployment function
main() {
    local method=${1:-"vercel"}
    
    echo "🎯 Deployment Method: $method"
    
    check_dependencies
    setup_environment
    install_frontend
    build_frontend
    install_backend
    test_application
    deploy $method
    
    print_status "Deployment completed successfully!"
    echo ""
    echo "🌐 Your Final Whistle AI application is now live!"
    echo "📝 Don't forget to:"
    echo "   1. Update your .env file with production values"
    echo "   2. Set up your Supabase database with the schema"
    echo "   3. Configure your domain and SSL certificates"
    echo "   4. Set up monitoring and logging"
}

# Run main function with arguments
main "$@"
