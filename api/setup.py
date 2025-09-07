#!/usr/bin/env python3
"""
Setup script for Football Focus API
Handles dependency installation and environment setup
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def setup_virtual_environment():
    """Set up virtual environment"""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print("🔧 Creating virtual environment...")
        if not run_command(f"{sys.executable} -m venv venv", "Creating virtual environment"):
            return False
    else:
        print("✅ Virtual environment already exists")
    
    return True

def install_dependencies():
    """Install dependencies with proper versions"""
    print("🔧 Installing dependencies...")
    
    # Determine the correct pip command based on OS
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        pip_cmd = "venv/bin/pip"
    
    # First, upgrade pip
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install dependencies one by one to avoid conflicts
    dependencies = [
        "Flask==3.0.0",
        "Flask-CORS==4.0.0",
        "python-dotenv==1.0.0",
        "Werkzeug==3.0.1",
        "httpx==0.25.2",
        "gotrue==2.5.0",
        "supabase==2.7.4"
    ]
    
    for dep in dependencies:
        if not run_command(f"{pip_cmd} install {dep}", f"Installing {dep}"):
            print(f"⚠️ Failed to install {dep}, trying to continue...")
    
    return True

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    template_file = Path("env_template.txt")
    
    if not env_file.exists() and template_file.exists():
        print("🔧 Creating .env file from template...")
        template_content = template_file.read_text()
        env_file.write_text(template_content)
        print("✅ .env file created")
        print("⚠️ Please edit .env file with your actual Supabase credentials")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️ No template file found, please create .env manually")

def verify_installation():
    """Verify that everything is installed correctly"""
    print("🔍 Verifying installation...")
    
    # Determine the correct python command
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        python_cmd = "venv/bin/python"
    
    test_script = """
import flask
import supabase
from dotenv import load_dotenv
print("✅ All dependencies imported successfully")
"""
    
    try:
        result = subprocess.run(
            [python_cmd, "-c", test_script],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Installation verification successful")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Installation verification failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Football Focus API...")
    print("=" * 50)
    
    # Change to the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    steps = [
        ("Setting up virtual environment", setup_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Creating environment file", create_env_file),
        ("Verifying installation", verify_installation)
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"❌ Setup failed at step: {step_name}")
            print("Please check the errors above and try again.")
            sys.exit(1)
    
    print("=" * 50)
    print("✅ Setup completed successfully!")
    print()
    print("Next steps:")
    print("1. Edit the .env file with your Supabase credentials")
    print("2. Run the API:")
    if os.name == 'nt':
        print("   venv\\Scripts\\python run.py")
    else:
        print("   venv/bin/python run.py")
    print("3. Test the API:")
    if os.name == 'nt':
        print("   venv\\Scripts\\python test_api.py")
    else:
        print("   venv/bin/python test_api.py")

if __name__ == "__main__":
    main()
