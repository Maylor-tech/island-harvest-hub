"""
Setup script for Island Harvest Hub AI Assistant.
"""

import os
import sys
import subprocess
import venv
from pathlib import Path

def create_virtual_environment():
    """Create a virtual environment."""
    print("Creating virtual environment...")
    venv.create("venv", with_pip=True)

def install_dependencies():
    """Install required packages."""
    print("Installing dependencies...")
    if sys.platform == "win32":
        pip_path = "venv\\Scripts\\pip"
    else:
        pip_path = "venv/bin/pip"
    
    subprocess.run([pip_path, "install", "-r", "island_harvest_hub/requirements.txt"])

def create_directories():
    """Create necessary directories."""
    print("Creating directories...")
    directories = [
        "island_harvest_hub/documents",
        "island_harvest_hub/documents/invoices",
        "island_harvest_hub/documents/reports",
        "island_harvest_hub/documents/contracts",
        "island_harvest_hub/documents/templates",
        "island_harvest_hub/documents/backups"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def initialize_database():
    """Initialize the database."""
    print("Initializing database...")
    if sys.platform == "win32":
        python_path = "venv\\Scripts\\python"
    else:
        python_path = "venv/bin/python"
    
    subprocess.run([python_path, "island_harvest_hub/init_db.py"])

def main():
    """Main setup function."""
    print("Starting Island Harvest Hub setup...")
    
    # Create virtual environment
    create_virtual_environment()
    
    # Install dependencies
    install_dependencies()
    
    # Create directories
    create_directories()
    
    # Initialize database
    initialize_database()
    
    print("\nSetup complete! To start the application:")
    print("1. Activate the virtual environment:")
    if sys.platform == "win32":
        print("   .\\venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Run the application:")
    print("   streamlit run island_harvest_hub/main.py")

if __name__ == "__main__":
    main() 