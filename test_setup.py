#!/usr/bin/env python3
"""
Quick test script to verify setup and test PDF mining on a single committee
"""

import sys
import os
import requests
from bs4 import BeautifulSoup
import PyPDF2
import pdfplumber
import pandas as pd
import matplotlib.pyplot as plt

def test_imports():
    """Test if all required packages are installed"""
    print("Testing package imports...")
    required_packages = {
        'requests': 'Web requests',
        'bs4': 'BeautifulSoup',
        'PyPDF2': 'PDF reading',
        'pdfplumber': 'Advanced PDF processing',
        'pandas': 'Data analysis',
        'openpyxl': 'Excel support',
        'matplotlib': 'Visualizations',
        'tqdm': 'Progress bars'
    }
    
    missing = []
    for package, description in required_packages.items():
        try:
            __import__(package)
            print(f"✓ {description} ({package})")
        except ImportError:
            print(f"✗ {description} ({package}) - MISSING")
            missing.append(package)
    
    # Test OCR packages (optional)
    print("\nTesting OCR packages (optional):")
    try:
        import pytesseract
        print("✓ pytesseract (OCR support)")
    except ImportError:
        print("⚠ pytesseract not installed (OCR will not work)")
    
    try:
        import pdf2image
        print("✓ pdf2image (PDF to image conversion)")
    except ImportError:
        print("⚠ pdf2image not installed (OCR will not work)")
    
    return len(missing) == 0

def test_website_access():
    """Test if we can access DeKalb County websites"""
    print("\nTesting website access...")
    test_url = "https://dekalbcounty.org/government/county-boards-commissions/finance/"
    
    try:
        response = requests.get(test_url, timeout=10)
        if response.status_code == 200:
            print(f"✓ Can access DeKalb County website")
            
            # Check if we can find PDFs
            soup = BeautifulSoup(response.content, 'html.parser')
            pdf_links = [a for a in soup.find_all('a', href=True) if a['href'].lower().endswith('.pdf')]
            print(f"✓ Found {len(pdf_links)} PDF links on the page")
            
            if pdf_links:
                # Try to access first PDF
                first_pdf = pdf_links[0]['href']
                if not first_pdf.startswith('http'):
                    first_pdf = f"https://dekalbcounty.org{first_pdf}"
                
                pdf_response = requests.head(first_pdf, timeout=10)
                if pdf_response.status_code == 200:
                    print(f"✓ Can access PDF files")
                    return True, first_pdf
            return True, None
        else:
            print(f"✗ Website returned status code: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"✗ Cannot access website: {e}")
        return False, None

def test_pdf_processing(pdf_url=None):
    """Test PDF download and text extraction"""
    print("\nTesting PDF processing...")
    
    if not pdf_url:
        # Use a test PDF if none provided
        print("⚠ No PDF URL available from website, skipping PDF test")
        return False
    
    try:
        # Download PDF
        print(f"Downloading test PDF...")
        response = requests.get(pdf_url, timeout=30)
        
        # Save temporarily
        test_pdf = "test_download.pdf"
        with open(test_pdf, 'wb') as f:
            f.write(response.content)
        print(f"✓ PDF downloaded successfully")
        
        # Test text extraction
        print("Testing text extraction...")
        text_extracted = False
        
        # Try pdfplumber
        try:
            with pdfplumber.open(test_pdf) as pdf:
                if pdf.pages:
                    text = pdf.pages[0].extract_text()
                    if text and len(text.strip()) > 50:
                        print(f"✓ Text extracted with pdfplumber: {len(text)} characters")
                        text_extracted = True
        except Exception as e:
            print(f"⚠ pdfplumber failed: {e}")
        
        # Try PyPDF2
        if not text_extracted:
            try:
                with open(test_pdf, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    if reader.pages:
                        text = reader.pages[0].extract_text()
                        if text and len(text.strip()) > 50:
                            print(f"✓ Text extracted with PyPDF2: {len(text)} characters")
                            text_extracted = True
            except Exception as e:
                print(f"⚠ PyPDF2 failed: {e}")
        
        # Clean up
        os.remove(test_pdf)
        
        return text_extracted
    except Exception as e:
        print(f"✗ PDF processing failed: {e}")
        return False

def test_output_generation():
    """Test if we can generate output files"""
    print("\nTesting output generation...")
    
    try:
        # Test Excel generation
        df = pd.DataFrame({
            'Committee': ['Test Committee'],
            'Finding': ['Test finding'],
            'Page': [1]
        })
        
        test_excel = "test_output.xlsx"
        df.to_excel(test_excel, index=False)
        print("✓ Excel file generation works")
        os.remove(test_excel)
        
        # Test visualization
        fig, ax = plt.subplots()
        ax.bar(['Test'], [1])
        test_image = "test_chart.png"
        plt.savefig(test_image)
        plt.close()
        print("✓ Chart generation works")
        os.remove(test_image)
        
        return True
    except Exception as e:
        print(f"✗ Output generation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("DEKALB COUNTY PDF MINER - SETUP TEST")
    print("=" * 60)
    
    results = []
    
    # Test 1: Package imports
    results.append(("Package Imports", test_imports()))
    
    # Test 2: Website access
    website_ok, pdf_url = test_website_access()
    results.append(("Website Access", website_ok))
    
    # Test 3: PDF processing
    if pdf_url:
        results.append(("PDF Processing", test_pdf_processing(pdf_url)))
    
    # Test 4: Output generation
    results.append(("Output Generation", test_output_generation()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All tests passed! You're ready to run the PDF miner.")
        print("\nNext steps:")
        print("1. Run the main script: python pdf_miner.py")
        print("2. Check the 'results' folder for output files")
        print("3. Review the log file 'pdf_miner.log' for details")
    else:
        print("\n⚠ Some tests failed. Please:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Check your internet connection")
        print("3. Verify Python version (3.8+ required)")
        
        if not website_ok:
            print("\n⚠ Website access failed. Possible issues:")
            print("  - Check internet connection")
            print("  - Website might be temporarily down")
            print("  - Firewall/proxy blocking access")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)