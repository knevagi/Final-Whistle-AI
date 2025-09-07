#!/usr/bin/env python3
"""
Startup script for Football Focus API with enhanced configuration
"""

import os
import sys
import argparse
from pathlib import Path

def setup_environment():
    """Setup environment and check dependencies"""
    
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  Warning: .env file not found!")
        print("   Please copy env_template.txt to .env and configure your settings")
        print("   Or set environment variables directly")
        print()
    
    # Check required environment variables
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file or environment")
        return False
    
    return True

def main():
    """Main startup function"""
    parser = argparse.ArgumentParser(
        description="Football Focus API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                    # Run in development mode
  python run.py --port 8000       # Run on custom port
  python run.py --production      # Run in production mode
  python run.py --test            # Test API endpoints
        """
    )
    
    parser.add_argument('--port', type=int, default=5000,
                       help='Port to run the server on (default: 5000)')
    parser.add_argument('--host', default='localhost',
                       help='Host to bind to (default: localhost)')
    parser.add_argument('--production', action='store_true',
                       help='Run in production mode')
    parser.add_argument('--test', action='store_true',
                       help='Test API endpoints after startup')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Set environment variables based on arguments
    if args.production:
        os.environ['FLASK_ENV'] = 'production'
        os.environ['DEBUG'] = 'False'
    else:
        os.environ['FLASK_ENV'] = 'development'
        os.environ['DEBUG'] = 'True'
    
    if args.debug:
        os.environ['DEBUG'] = 'True'
    
    os.environ['PORT'] = str(args.port)
    
    # Test endpoints if requested
    if args.test:
        print("🧪 Testing API endpoints...")
        import subprocess
        result = subprocess.run([sys.executable, 'test_api.py', f'http://{args.host}:{args.port}'])
        return result.returncode
    
    # Import and run the Flask app
    try:
        from app import app, api
        
        print("🚀 Starting Football Focus API...")
        print(f"📍 Server: http://{args.host}:{args.port}")
        print(f"🔧 Environment: {os.getenv('FLASK_ENV', 'development')}")
        print(f"🐛 Debug: {os.getenv('DEBUG', 'False')}")
        
        # Test database connection
        print("🔍 Testing database connection...")
        test_result = api.supabase.table('generated_articles').select('id').limit(1).execute()
        print("✅ Database connection successful")
        
        # Show available endpoints
        print("\n📋 Available endpoints:")
        print("   GET  /health")
        print("   GET  /api/articles")
        print("   GET  /api/articles/{id}")
        print("   GET  /api/categories")
        print("   GET  /api/featured")
        print("   GET  /api/trending")
        print("   GET  /api/stats")
        print()
        
        # Start the server
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug or os.getenv('DEBUG', 'False').lower() == 'true'
        )
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
