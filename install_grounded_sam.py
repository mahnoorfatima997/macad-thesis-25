#!/usr/bin/env python3
"""
Installation script for Grounded SAM integration
Sets up dependencies and tests the installation
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8 or higher.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Core dependencies
    dependencies = [
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "transformers>=4.30.0",
        "supervision>=0.18.0",
        "accelerate>=0.20.0",
        "opencv-python>=4.10.0",
        "Pillow>=10.4.0",
        "numpy>=1.26.4"
    ]
    
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            return False
    
    return True

def test_imports():
    """Test if all required modules can be imported"""
    print("\n🧪 Testing imports...")
    
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
        
        import transformers
        print(f"✅ Transformers {transformers.__version__}")
        
        import supervision
        print(f"✅ Supervision {supervision.__version__}")
        
        import cv2
        print(f"✅ OpenCV {cv2.__version__}")
        
        import PIL
        print(f"✅ Pillow {PIL.__version__}")
        
        import numpy
        print(f"✅ NumPy {numpy.__version__}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_model_download():
    """Test model download functionality"""
    print("\n📥 Testing model download...")
    
    try:
        from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
        
        # Test Grounding DINO model download
        print("🔄 Downloading Grounding DINO model...")
        processor = AutoProcessor.from_pretrained("IDEA-Research/grounding-dino-tiny")
        model = AutoModelForZeroShotObjectDetection.from_pretrained("IDEA-Research/grounding-dino-tiny")
        print("✅ Grounding DINO model downloaded successfully")
        
        # Test SAM2 model download
        print("🔄 Downloading SAM2 model...")
        from transformers import SamProcessor, SamModel
        sam_processor = SamProcessor.from_pretrained("facebook/sam-vit-huge")
        sam_model = SamModel.from_pretrained("facebook/sam-vit-huge")
        print("✅ SAM2 model downloaded successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Model download failed: {e}")
        return False

def create_test_script():
    """Create a simple test script"""
    print("\n📝 Creating test script...")
    
    test_script = '''#!/usr/bin/env python3
"""
Quick test for Grounded SAM installation
"""

import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

try:
    from src.core.detection.grounded_sam_module import GroundedSAMDetector
    print("✅ Grounded SAM module imported successfully")
    
    # Test initialization
    detector = GroundedSAMDetector()
    print("✅ Grounded SAM detector initialized successfully")
    
    print("\\n🎉 Installation test completed successfully!")
    print("You can now use Grounded SAM for architectural analysis.")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    sys.exit(1)
'''
    
    with open("test_installation.py", "w") as f:
        f.write(test_script)
    
    print("✅ Test script created: test_installation.py")

def main():
    """Main installation function"""
    print("🚀 Grounded SAM Installation Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Dependency installation failed. Please check the errors above.")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Please check the errors above.")
        sys.exit(1)
    
    # Test model download
    if not test_model_download():
        print("\n❌ Model download failed. Please check the errors above.")
        sys.exit(1)
    
    # Create test script
    create_test_script()
    
    print("\n🎉 Installation completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run: python test_installation.py")
    print("2. Run: python test_grounded_sam.py")
    print("3. Check the GROUNDED_SAM_README.md for usage examples")
    
    print("\n💡 Tips:")
    print("- Use GPU if available for better performance")
    print("- Adjust thresholds based on your needs")
    print("- Check the README for configuration options")

if __name__ == "__main__":
    main() 