#!/usr/bin/env python3
"""
Installation helper for DeKalb County PDF Mining Tool
Handles Python 3.13 compatibility and step-by-step installation
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n{description}...")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✓ {description} successful")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        return False

def main():
    print("=" * 60)
    print("DEKALB PDF MINER - INSTALLATION HELPER")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("\n✗ Python 3.8+ is required")
        sys.exit(1)
    
    if sys.version_info >= (3, 13):
        print("\n⚠ Python 3.13 detected - using compatible package versions")
    
    # Upgrade pip first
    print("\nStep 1: Upgrading pip...")
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Pip upgrade")
    
    # Install packages one by one for better error handling
    packages = [
        # Core packages that should work
        ("requests", "Web requests library"),
        ("beautifulsoup4", "HTML parsing library"),
        ("tqdm", "Progress bars"),
        ("python-dateutil", "Date utilities"),
        ("chardet", "Character encoding detection"),
        
        # PDF packages
        ("PyPDF2", "PDF reading library"),
        
        # Data packages
        ("openpyxl", "Excel file support"),
        
        # These might need special handling
        ("lxml", "XML/HTML processing"),
        ("numpy", "Numerical computing"),
        ("pandas", "Data analysis"),
        ("matplotlib", "Plotting library"),
        ("seaborn", "Statistical visualization"),
        
        # PDF advanced processing
        ("pdfplumber", "Advanced PDF extraction"),
        
        # Image processing (might fail, that's OK)
        ("Pillow", "Image processing library"),
        ("pdf2image", "PDF to image conversion"),
        ("pytesseract", "OCR capabilities"),
    ]
    
    print("\nStep 2: Installing packages...")
    failed = []
    optional_failed = []
    
    for package, description in packages:
        success = run_command(
            f"{sys.executable} -m pip install {package}",
            f"Installing {description}"
        )
        if not success:
            if package in ["pytesseract", "pdf2image", "Pillow"]:
                optional_failed.append(package)
            else:
                failed.append(package)
    
    print("\n" + "=" * 60)
    print("INSTALLATION SUMMARY")
    print("=" * 60)
    
    if not failed:
        print("\n✓ Core packages installed successfully!")
        
        if optional_failed:
            print(f"\n⚠ Optional packages failed to install: {', '.join(optional_failed)}")
            print("  These are only needed for OCR of scanned PDFs.")
            print("  The tool will still work for text-based PDFs.")
        
        print("\n✓ You're ready to run the PDF miner!")
        print("\nNext steps:")
        print("1. Test your setup: python test_setup.py")
        print("2. Quick test: python quick_start.py")
        print("3. Full analysis: python pdf_miner.py")
    else:
        print(f"\n✗ Failed to install required packages: {', '.join(failed)}")
        print("\nTroubleshooting:")
        print("1. Try installing Visual Studio Build Tools (for Windows)")
        print("   Download from: https://visualstudio.microsoft.com/downloads/")
        print("2. Or try using conda instead of pip:")
        print("   conda install pandas numpy matplotlib")
        print("3. Or use a different Python version (3.10 or 3.11 recommended)")
    
    return len(failed) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)