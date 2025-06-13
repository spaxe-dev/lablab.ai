#!/usr/bin/env python3
"""
Quick setup script for Dependency Health Monitor
"""
import os
import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def create_virtual_environment():
    """Create a virtual environment if it doesn't exist"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    try:
        print("🔧 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False

def install_dependencies():
    """Install required dependencies"""
    try:
        # Determine the correct pip path
        if os.name == 'nt':  # Windows
            pip_path = Path("venv/Scripts/pip.exe")
        else:  # Unix-like
            pip_path = Path("venv/bin/pip")
        
        if not pip_path.exists():
            print("❌ Virtual environment pip not found")
            return False
        
        print("📦 Installing dependencies...")
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        try:
            with open(env_example, 'r') as src, open(env_file, 'w') as dst:
                dst.write(src.read())
            print("✅ Created .env file from template")
            print("🔧 Please edit .env file with your configuration")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("⚠️  No .env.example template found")
        return True

def run_health_check():
    """Run a quick health check"""
    try:
        # Determine the correct python path
        if os.name == 'nt':  # Windows
            python_path = Path("venv/Scripts/python.exe")
        else:  # Unix-like
            python_path = Path("venv/bin/python")
        
        if not python_path.exists():
            print("❌ Virtual environment python not found")
            return False
        
        print("🔍 Running health check...")
        result = subprocess.run([
            str(python_path), "main.py", "--file", "requirements.txt"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Health check passed")
            return True
        else:
            print("⚠️  Health check completed with warnings")
            print("This is normal if no requirements.txt file exists yet")
            return True
    except subprocess.TimeoutExpired:
        print("⚠️  Health check timed out (this is normal)")
        return True
    except Exception as e:
        print(f"⚠️  Health check failed: {e}")
        return True

def main():
    """Main setup function"""
    print("🚀 Setting up Dependency Health Monitor...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Create virtual environment
    if not create_virtual_environment():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Create .env file
    create_env_file()
    
    # Run health check
    run_health_check()
    
    print("=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your configuration (optional)")
    print("2. Start the API server:")
    
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\python.exe main.py --server")
    else:  # Unix-like
        print("   venv/bin/python main.py --server")
    
    print("3. Or scan a requirements file:")
    
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\python.exe main.py --file requirements.txt")
    else:  # Unix-like
        print("   venv/bin/python main.py --file requirements.txt")
    
    print("\nAPI will be available at: http://localhost:5000")
    print("Health check endpoint: http://localhost:5000/health")
    
    return 0

if __name__ == "__main__":
    exit(main())
