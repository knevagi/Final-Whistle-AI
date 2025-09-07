#!/usr/bin/env python3
"""
Setup script for the English Football Fixture Service
This script helps users quickly configure and start the service.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("⚽ English Football Fixture Service Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("   Please install Python 3.8 or higher")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print(f"Error output: {e.stderr}")
        return False

def setup_environment():
    """Set up environment file"""
    print("\n🔧 Setting up environment...")
    
    env_file = Path('.env')
    env_template = Path('env_template.txt')
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("Keeping existing .env file")
            return True
    
    if not env_template.exists():
        print("❌ env_template.txt not found")
        return False
    
    try:
        # Copy template
        with open(env_template, 'r') as f:
            template_content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(template_content)
        
        print("✅ Created .env file from template")
        print("📝 Please edit .env file with your API keys:")
        print("   - SUPABASE_URL")
        print("   - SUPABASE_KEY")
        print("   - OPENAI_API_KEY")
        print("   - SERPER_API_KEY")
        print("   - API_FOOTBALL_KEY (optional)")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def setup_supabase():
    """Guide user through Supabase setup"""
    print("\n🗄️  Supabase Database Setup")
    print("=" * 40)
    print("To set up Supabase:")
    print("1. Go to https://supabase.com/")
    print("2. Create a new project")
    print("3. Go to Settings > Database")
    print("4. Copy the connection string")
    print("5. Go to Settings > API")
    print("6. Copy the anon/public key")
    print("7. Go to SQL Editor")
    print("8. Run the contents of schema.sql")
    print()
    
    response = input("Have you set up Supabase? (y/N): ").lower()
    if response == 'y':
        print("✅ Supabase setup confirmed")
        return True
    else:
        print("⚠️  Please complete Supabase setup before continuing")
        return False

def get_api_keys():
    """Guide user through API key setup"""
    print("\n🔑 API Keys Setup")
    print("=" * 40)
    
    print("Required API Keys:")
    print("1. OpenAI API Key: https://platform.openai.com/api-keys")
    print("2. Serper API Key: https://serper.dev/")
    print("3. API Football Key (optional): https://rapidapi.com/api-sports/api/api-football/")
    print()
    
    print("Please add your API keys to the .env file:")
    print("- OPENAI_API_KEY=your_key_here")
    print("- SERPER_API_KEY=your_key_here")
    print("- API_FOOTBALL_KEY=your_key_here (optional)")
    print()
    
    response = input("Have you added your API keys to .env? (y/N): ").lower()
    if response == 'y':
        print("✅ API keys configured")
        return True
    else:
        print("⚠️  Please add API keys to .env file")
        return False

def run_tests():
    """Run setup tests"""
    print("\n🧪 Running setup tests...")
    try:
        result = subprocess.run([sys.executable, "test_setup.py"], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Some tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def show_next_steps():
    """Show next steps after setup"""
    print("\n🎉 Setup Complete!")
    print("=" * 40)
    print("Next steps:")
    print()
    print("1. Test the service:")
    print("   python run_service.py --test")
    print()
    print("2. Show configuration:")
    print("   python run_service.py --config")
    print()
    print("3. Run the service:")
    print("   python run_service.py --full")
    print()
    print("4. Monitor logs:")
    print("   tail -f fixture_service.log")
    print()
    print("For more information, see README.md")

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("❌ Setup failed at environment setup")
        sys.exit(1)
    
    # Guide through Supabase setup
    if not setup_supabase():
        print("❌ Setup failed at Supabase setup")
        sys.exit(1)
    
    # Guide through API key setup
    if not get_api_keys():
        print("❌ Setup failed at API key setup")
        sys.exit(1)
    
    # Run tests
    if not run_tests():
        print("❌ Setup failed at testing")
        print("Please fix the issues and run setup again")
        sys.exit(1)
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)
