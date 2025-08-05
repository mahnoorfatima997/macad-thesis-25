"""
Setup script for MEGA Test System
Handles installation of dependencies and configuration
"""

import subprocess
import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == "win32":
    import locale
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n📦 {description}...")
    try:
        subprocess.run(cmd, check=True, shell=True)
        print(f"✅ {description} - Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed!")
        print(f"   Error: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def setup_test_system():
    """Setup the MEGA test system"""
    print("🚀 MEGA Test System Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check if we're in the right directory
    if not Path("thesis_tests").exists():
        print("❌ Error: 'thesis_tests' directory not found")
        print("   Please run this script from the project root directory")
        return False
    
    # Update pip
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Updating pip")
    
    # Install main requirements
    requirements_file = "thesis_tests/requirements_tests.txt"
    if Path(requirements_file).exists():
        success = run_command(
            f"{sys.executable} -m pip install -r {requirements_file}",
            "Installing test system requirements"
        )
        if not success:
            print("\n💡 Tip: If you're having issues, try creating a virtual environment:")
            print("   python -m venv test_env")
            print("   test_env\\Scripts\\activate  (Windows)")
            print("   source test_env/bin/activate  (Linux/Mac)")
            return False
    else:
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    # Install spaCy language model
    print("\n📦 Installing spaCy language model...")
    success = run_command(
        f"{sys.executable} -m spacy download en_core_web_sm",
        "Downloading spaCy English model"
    )
    
    # Create necessary directories
    print("\n📁 Creating data directories...")
    directories = [
        "thesis_tests/test_data",
        "thesis_tests/linkography_data",
        "thesis_tests/uploads",
        "benchmarking/data/sessions"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created: {dir_path}")
    
    # Check for .env file
    if not Path(".env").exists():
        print("\n⚠️  Warning: .env file not found")
        print("   Please create a .env file with your OpenAI API key:")
        print("   OPENAI_API_KEY=your-api-key-here")
        print("\n   The Generic AI test environment requires this key.")
    
    # Final instructions
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\nTo run the test dashboard:")
    print(f"   {sys.executable} launch_test_dashboard.py")
    print("\nOr directly with streamlit:")
    print("   streamlit run thesis_tests/test_dashboard.py")
    
    return True

def main():
    """Main entry point"""
    try:
        success = setup_test_system()
        if not success:
            print("\n❌ Setup failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()