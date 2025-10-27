#!/usr/bin/env python3
"""
Quick start script - Tests the PDF miner on just the Highway Committee
This is useful for testing the setup and getting initial results quickly
"""

import os
import re
import requests
from bs4 import BeautifulSoup
import PyPDF2
import pdfplumber
import pandas as pd
from datetime import datetime
import json

def search_single_pdf(url, keywords):
    """Download and search a single PDF"""
    results = []
    
    try:
        # Download PDF
        print(f"  Downloading: {os.path.basename(url)}")
        response = requests.get(url, timeout=30)
        
        # Save temporarily
        temp_pdf = "temp_search.pdf"
        with open(temp_pdf, 'wb') as f:
            f.write(response.content)
        
        # Extract text
        all_text = ""
        page_texts = []
        
        # Try pdfplumber first
        try:
            with pdfplumber.open(temp_pdf) as pdf:
                for i, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        page_texts.append((i, text))
                        all_text += text + "\n"
        except:
            # Fallback to PyPDF2
            with open(temp_pdf, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for i, page in enumerate(reader.pages, 1):
                    text = page.extract_text()
                    if text:
                        page_texts.append((i, text))
                        all_text += text + "\n"
        
        # Search for keywords
        for page_num, page_text in page_texts:
            for keyword in keywords:
                if re.search(keyword, page_text, re.IGNORECASE):
                    # Get context
                    matches = re.finditer(keyword, page_text, re.IGNORECASE)
                    for match in matches:
                        start = max(0, match.start() - 150)
                        end = min(len(page_text), match.end() + 150)
                        context = page_text[start:end].strip()
                        context = ' '.join(context.split())  # Clean whitespace
                        
                        results.append({
                            'pdf': os.path.basename(url),
                            'page': page_num,
                            'keyword': keyword,
                            'matched': match.group(),
                            'context': context
                        })
        
        # Clean up
        os.remove(temp_pdf)
        
        if results:
            print(f"    ✓ Found {len(results)} matches")
        else:
            print(f"    - No matches found")
            
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    return results

def quick_highway_search():
    """Quick search of Highway Committee for key terms"""
    
    print("=" * 60)
    print("QUICK HIGHWAY COMMITTEE SEARCH")
    print("Testing for Steve Hamm and related keywords")
    print("=" * 60)
    
    # Priority keywords to search
    keywords = [
        r'\bSteve\s+Hamm\b',
        r'\bS\.\s*Hamm\b',
        r'\bHamm\b',
        r'\bethics\s+training\b',
        r'\babuse\s+of\s+(authority|position)\b',
        r'\bG-K\s+Broncos\b',
        r'\bKingston\s+Park\b',
        r'\btrailer\b',
        r'\bpersonal\s+use\b',
        r'\bmisconduct\b',
        r'\binvestigation\b',
        r'\bcomplaint\b'
    ]
    
    # Highway Committee URLs
    main_url = 'https://dekalbcounty.org/government/county-boards-commissions/county-highway/'
    archive_url = 'https://dekalbcounty.org/government/county-boards-commissions/county-highway/highway-committee-archive/'
    
    all_results = []
    
    # Process main page
    print(f"\nChecking main Highway Committee page...")
    try:
        response = requests.get(main_url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        pdf_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].lower().endswith('.pdf')]
        
        print(f"Found {len(pdf_links)} PDFs on main page")
        
        # Process first 5 PDFs as a test
        for pdf_link in pdf_links[:5]:
            if not pdf_link.startswith('http'):
                pdf_link = f"https://dekalbcounty.org{pdf_link}"
            
            results = search_single_pdf(pdf_link, keywords)
            all_results.extend(results)
            
    except Exception as e:
        print(f"Error accessing main page: {e}")
    
    # Process archive page
    print(f"\nChecking Highway Committee archive page...")
    try:
        response = requests.get(archive_url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        pdf_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].lower().endswith('.pdf')]
        
        print(f"Found {len(pdf_links)} PDFs in archive")
        
        # Look for PDFs from 2023-2024 specifically
        recent_pdfs = []
        for link in soup.find_all('a', href=True):
            if link['href'].lower().endswith('.pdf'):
                text = link.get_text()
                if '2023' in text or '2024' in text:
                    pdf_url = link['href']
                    if not pdf_url.startswith('http'):
                        pdf_url = f"https://dekalbcounty.org{pdf_url}"
                    recent_pdfs.append(pdf_url)
        
        print(f"Found {len(recent_pdfs)} PDFs from 2023-2024")
        
        # Process recent PDFs
        for pdf_link in recent_pdfs[:10]:  # Limit to 10 for quick test
            results = search_single_pdf(pdf_link, keywords)
            all_results.extend(results)
            
    except Exception as e:
        print(f"Error accessing archive page: {e}")
    
    # Generate report
    print("\n" + "=" * 60)
    print("SEARCH RESULTS")
    print("=" * 60)
    
    if all_results:
        print(f"\nTotal matches found: {len(all_results)}")
        
        # Group by keyword
        keyword_counts = {}
        for result in all_results:
            keyword = result['keyword']
            if keyword not in keyword_counts:
                keyword_counts[keyword] = []
            keyword_counts[keyword].append(result)
        
        print("\nMatches by keyword:")
        for keyword, matches in keyword_counts.items():
            print(f"  {keyword}: {len(matches)} matches")
        
        # Show high-priority findings
        print("\n" + "-" * 40)
        print("HIGH PRIORITY FINDINGS (First 5):")
        print("-" * 40)
        
        # Look for Steve Hamm mentions specifically
        hamm_results = [r for r in all_results if 'Hamm' in r['matched']]
        
        for i, result in enumerate(hamm_results[:5], 1):
            print(f"\n#{i}")
            print(f"PDF: {result['pdf']}")
            print(f"Page: {result['page']}")
            print(f"Matched: '{result['matched']}'")
            print(f"Context: ...{result['context'][:200]}...")
        
        # Save results to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save as JSON
        json_file = f'highway_quick_results_{timestamp}.json'
        with open(json_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"\nFull results saved to: {json_file}")
        
        # Save as Excel
        df = pd.DataFrame(all_results)
        excel_file = f'highway_quick_results_{timestamp}.xlsx'
        df.to_excel(excel_file, index=False)
        print(f"Excel report saved to: {excel_file}")
        
    else:
        print("\nNo matches found in the PDFs searched.")
        print("This could mean:")
        print("  1. The keywords don't appear in recent minutes")
        print("  2. The PDFs might be scanned images (need OCR)")
        print("  3. The search terms need adjustment")
    
    print("\n" + "=" * 60)
    print("Quick search complete!")
    print("For full analysis of all committees and archives,")
    print("run the main script: python pdf_miner.py")
    print("=" * 60)

if __name__ == "__main__":
    quick_highway_search()