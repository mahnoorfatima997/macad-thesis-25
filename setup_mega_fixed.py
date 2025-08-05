#!/usr/bin/env python3
"""
Fixed Setup Script for Mega Architectural Mentor
Handles dependency installation in correct order to avoid conflicts
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("🏗️  Mega Architectural Mentor - Fixed Setup Script")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def create_virtual_environment():
    """Create virtual environment"""
    print("🔧 Creating virtual environment...")
    venv_name = "mega_env"
    
    if os.path.exists(venv_name):
        print(f"⚠️  Virtual environment '{venv_name}' already exists")
        response = input("   Do you want to recreate it? (y/N): ")
        if response.lower() == 'y':
            import shutil
            shutil.rmtree(venv_name)
            print(f"   Removed existing virtual environment")
        else:
            print("   Using existing virtual environment")
            return venv_name
    
    try:
        subprocess.run([sys.executable, "-m", "venv", venv_name], check=True)
        print(f"✅ Virtual environment '{venv_name}' created")
        return venv_name
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return None

def get_venv_pip(venv_name):
    """Get path to virtual environment pip"""
    if platform.system() == "Windows":
        return os.path.join(venv_name, "Scripts", "pip.exe")
    else:
        return os.path.join(venv_name, "bin", "pip")

def install_packages_in_order(venv_name):
    """Install packages in the correct order to avoid conflicts"""
    print("📦 Installing packages in order...")
    pip_path = get_venv_pip(venv_name)
    
    # Step 1: Upgrade pip
    print("   ⬆️  Upgrading pip...")
    try:
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        print("   ✅ Pip upgraded")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to upgrade pip: {e}")
        return False
    
    # Step 2: Install basic packages first
    print("   📦 Installing basic packages...")
    basic_packages = [
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0"
    ]
    
    for package in basic_packages:
        try:
            subprocess.run([pip_path, "install", package], check=True)
            print(f"   ✅ Installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install {package}: {e}")
            return False
    
    # Step 3: Install PyTorch first
    print("   🔥 Installing PyTorch...")
    try:
        # Install PyTorch with CPU support (more reliable)
        subprocess.run([pip_path, "install", "torch", "torchvision", "--index-url", "https://download.pytorch.org/whl/cpu"], check=True)
        print("   ✅ PyTorch installed")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to install PyTorch: {e}")
        return False
    
    # Step 4: Install other ML packages
    print("   🤖 Installing ML packages...")
    ml_packages = [
        "transformers>=4.30.0",
        "openai>=1.0.0",
        "langgraph>=0.0.20",
        "langchain>=0.1.0",
        "langchain-openai>=0.0.5"
    ]
    
    for package in ml_packages:
        try:
            subprocess.run([pip_path, "install", package], check=True)
            print(f"   ✅ Installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install {package}: {e}")
            return False
    
    # Step 5: Install vision packages
    print("   👁️  Installing vision packages...")
    vision_packages = [
        "opencv-python>=4.8.0",
        "pillow>=10.0.0",
        "imageio>=2.31.0"
    ]
    
    for package in vision_packages:
        try:
            subprocess.run([pip_path, "install", package], check=True)
            print(f"   ✅ Installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install {package}: {e}")
            return False
    
    # Step 6: Install Streamlit and other packages
    print("   🌐 Installing web interface...")
    web_packages = [
        "streamlit>=1.28.0",
        "chromadb>=0.4.0",
        "sentence-transformers>=2.2.0"
    ]
    
    for package in web_packages:
        try:
            subprocess.run([pip_path, "install", package], check=True)
            print(f"   ✅ Installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install {package}: {e}")
            return False
    
    # Step 7: Install remaining packages
    print("   📚 Installing remaining packages...")
    remaining_packages = [
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "scikit-learn>=1.3.0",
        "aiohttp>=3.8.0",
        "orjson>=3.9.0",
        "asyncio-mqtt>=0.13.0",
        "python-decouple>=3.8"
    ]
    
    for package in remaining_packages:
        try:
            subprocess.run([pip_path, "install", package], check=True)
            print(f"   ✅ Installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install {package}: {e}")
            return False
    
    print("   ✅ All packages installed successfully!")
    return True



def create_env_file():
    """Create .env file template"""
    print("🔑 Creating .env file template...")
    
    if os.path.exists(".env"):
        print("⚠️  .env file already exists")
        response = input("   Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("   Keeping existing .env file")
            return True
    
    env_content = """# Mega Architectural Mentor Environment Variables
# Add your OpenAI API key here
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Logging configuration
# LOG_LEVEL=INFO       # Options: DEBUG, INFO, WARNING, ERROR
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ .env file created")
        print("   ⚠️  Please add your OpenAI API key to the .env file")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = [
        "uploads",
        "outputs",
        "logs",
        "cache"
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Failed to create directory {directory}: {e}")

def test_installation(venv_name):
    """Test the installation"""
    print("🧪 Testing installation...")
    python_path = get_venv_python(venv_name)
    
    test_script = """
import sys
print("Testing imports...")

try:
    import streamlit
    print("✅ Streamlit imported successfully")
except ImportError as e:
    print(f"❌ Streamlit import failed: {e}")

try:
    import torch
    print("✅ PyTorch imported successfully")
    print(f"   CUDA available: {torch.cuda.is_available()}")
except ImportError as e:
    print(f"❌ PyTorch import failed: {e}")

try:
    import transformers
    print("✅ Transformers imported successfully")
except ImportError as e:
    print(f"❌ Transformers import failed: {e}")

try:
    import openai
    print("✅ OpenAI imported successfully")
except ImportError as e:
    print(f"❌ OpenAI import failed: {e}")

try:
    import cv2
    print("✅ OpenCV imported successfully")
except ImportError as e:
    print(f"❌ OpenCV import failed: {e}")

try:
    import langchain
    print("✅ LangChain imported successfully")
except ImportError as e:
    print(f"❌ LangChain import failed: {e}")

print("\\nInstallation test complete!")
"""
    
    try:
        result = subprocess.run([python_path, "-c", test_script], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation test failed: {e}")
        print(f"   Error output: {e.stderr}")
        return False

def get_venv_python(venv_name):
    """Get path to virtual environment Python"""
    if platform.system() == "Windows":
        return os.path.join(venv_name, "Scripts", "python.exe")
    else:
        return os.path.join(venv_name, "bin", "python")

def print_activation_instructions(venv_name):
    """Print activation instructions"""
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("=" * 60)
    print()
    print("To activate the virtual environment:")
    
    if platform.system() == "Windows":
        print(f"   {venv_name}\\Scripts\\activate")
    else:
        print(f"   source {venv_name}/bin/activate")
    
    print()
    print("To run the Mega Architectural Mentor:")
    print("   1. Activate the virtual environment")
    print("   2. Add your OpenAI API key to the .env file")
    print("   3. Run: streamlit run mega_architectural_mentor.py")
    print()
    print("For more information, see README_MEGA.md")
    print()

def main():
    """Main setup function"""
    print_banner()
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    print()
    
    # Create virtual environment
    venv_name = create_virtual_environment()
    if not venv_name:
        return False
    
    print()
    
    # Install packages in order
    if not install_packages_in_order(venv_name):
        return False
    
    print()
    

    
    print()
    
    # Create .env file
    if not create_env_file():
        return False
    
    print()
    
    # Create directories
    create_directories()
    
    print()
    
    # Test installation
    if not test_installation(venv_name):
        print("⚠️  Installation test failed, but setup may still work")
        print("   Try running the app and see if it works")
    
    print()
    
    # Print instructions
    print_activation_instructions(venv_name)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Setup failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        sys.exit(1) 