"""
Setup script for the Autonomous Cognitive Engine project.
"""
import subprocess
import sys
import os

def install_uv():
    """Install uv package manager if not already installed."""
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        print(" uv is already installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(" Installing uv package manager...")
        try:
            # Install uv using pip
            subprocess.run([sys.executable, "-m", "pip", "install", "uv"], check=True)
            print(" uv installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f" Failed to install uv: {e}")
            return False

def setup_environment():
    """Set up the project environment."""
    print(" Setting up Autonomous Cognitive Engine environment...")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print(" Python 3.11+ is required")
        return False
    
    print(f" Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install uv
    if not install_uv():
        print("  Falling back to pip for package installation")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print(" Dependencies installed with pip")
        except subprocess.CalledProcessError as e:
            print(f" Failed to install dependencies: {e}")
            return False
    else:
        # Use uv to install dependencies
        try:
            subprocess.run(["uv", "pip", "install", "-r", "requirements.txt"], check=True)
            print(" Dependencies installed with uv")
        except subprocess.CalledProcessError as e:
            print(f" Failed to install dependencies with uv: {e}")
            return False
    
    # Check for .env file
    if not os.path.exists(".env"):
        print(" Creating .env file from template...")
        try:
            with open(".env.example", "r") as example:
                content = example.read()
            with open(".env", "w") as env_file:
                env_file.write(content)
            print(" .env file created. Please add your API keys.")
        except Exception as e:
            print(f" Could not create .env file: {e}")
    else:
        print(" .env file already exists")
    
    print("\n Setup complete!")
    print("\nNext steps:")
    print("1. Add your API keys to the .env file:")
    print(f"   - ANTHROPIC_API_KEY (required)")
    print(f"   - TAVILY_API_KEY (optional, for web search)")
    print(f"   - LANGCHAIN_API_KEY (optional, for LangSmith tracing)")
    print("2. Run: python main.py")
    print("3. Or test Milestone 1: python test_milestone1.py")
    
    return True

if __name__ == "__main__":
    setup_environment()