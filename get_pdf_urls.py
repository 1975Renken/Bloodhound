#!/usr/bin/env python3
"""
Extract PDF URLs from DeKalb County websites
Generates a list of URLs you can download manually or with a download manager
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import json
from datetime import datetime

def get_pdf_urls():
    """Extract all PDF URLs from DeKalb County committee pages"""
    
    # Committee pages
    committees = {
        'Finance & Administration': {
            'main': 'https://dekalbcounty.org/government/county-boards-commissions/finance/',
            'archive': 'https://dekalbcounty.org/government/county-boards-commissions/finance/finance-committee-archive/'
        },
        'Highway': {
            'main': 'https://dekalbcounty.org/government/county-boards-commissions/county-highway/',
            'archive': 'https://dekalbcounty.org/government/county-boards-commissions/county-highway/highway-committee-archive/'
        },
        'Law & Justice': {
            'main': 'https://dekalbcounty.org/government/county-boards-commissions/law-justice/',
            'archive': 'https://dekalbcounty.org/government/county-boards-commissions/law-justice/law-justice-archive/'
        },
        'Committee of the Whole': {
            'main': 'https://dekalbcounty.org/government/county-boards-commissions/committee-of-the-whole/',
            'archive': 'https://dekalbcounty.org/government/county-boards-commissions/committee-of-the-whole/committee-of-the-whole-archive/'
        },
        'Executive': {
            'main': 'https://dekalbcounty.org/government/county-boards-commissions/executive/',
            'archive': 'https://dekalbcounty.org/government/county-boards-commissions/executive/executive-committee-archive/'
        },
        'County Board': {
            'main': 'https://dekalbcounty.org/government/county-boards-commissions/county-board-meetings/',
            'archive': 'https://dekalbcounty.org/government/county-boards-commissions/county-board-meetings/county-board-archives/'
        },
        'Board of Review': {
            'main': 'https://dekalbcounty.org/departments/assessment-office/board-of-review/board-of-review-meetings/',
            'archive': 'https://dekalbcounty.org/departments/assessment-office/board-of-review/board-of-review-meetings/board-of-review-archives/'
        }
    }
    
    all_pdfs = []
    
    print("=" * 60)
    print("EXTRACTING PDF URLS FROM DEKALB COUNTY WEBSITES")
    print("=" * 60)
    
    # Try to get PDFs from each committee
    for committee_name, urls in committees.items():
        print(f"\nProcessing {committee_name}...")
        
        for page_type, url in urls.items():
            print(f"  Checking {page_type} page: {url}")
            
            try:
                # Try with minimal headers first
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find all PDF links
                    pdf_count = 0
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if href.lower().endswith('.pdf'):
                            full_url = urljoin(url, href)
                            link_text = link.get_text(strip=True)
                            
                            all_pdfs.append({
                                'committee': committee_name,
                                'page_type': page_type,
                                'url': full_url,
                                'text': link_text,
                                'source_page': url
                            })
                            pdf_count += 1
                    
                    print(f"    ✓ Found {pdf_count} PDFs")
                    
                elif response.status_code == 403:
                    print(f"    ✗ Access blocked (403)")
                else:
                    print(f"    ✗ Error: {response.status_code}")
                    
            except Exception as e:
                print(f"    ✗ Error: {e}")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if all_pdfs:
        # Save as CSV
        csv_file = f'pdf_urls_{timestamp}.csv'
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['committee', 'page_type', 'text', 'url', 'source_page'])
            writer.writeheader()
            writer.writerows(all_pdfs)
        
        # Save as JSON
        json_file = f'pdf_urls_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_pdfs, f, indent=2)
        
        # Save as simple text list
        txt_file = f'pdf_urls_{timestamp}.txt'
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("PDF URLs from DeKalb County Committees\n")
            f.write("=" * 60 + "\n\n")
            for pdf in all_pdfs:
                f.write(f"{pdf['committee']} - {pdf['text']}\n")
                f.write(f"{pdf['url']}\n\n")
        
        print("\n" + "=" * 60)
        print(f"FOUND {len(all_pdfs)} PDF URLs")
        print("=" * 60)
        print(f"\nFiles saved:")
        print(f"  - {csv_file} (spreadsheet format)")
        print(f"  - {json_file} (data format)")
        print(f"  - {txt_file} (simple list)")
        
        print("\nYou can now:")
        print("1. Open the text file and copy URLs to a download manager")
        print("2. Use the CSV file to track which PDFs you've downloaded")
        print("3. Manually download PDFs through your browser")
        
    else:
        print("\n" + "=" * 60)
        print("NO PDFs FOUND")
        print("=" * 60)
        print("\nThe website appears to be blocking automated access.")
        print("\nAlternative approach:")
        print("1. Open each committee URL in your browser")
        print("2. Right-click and 'Save As' each PDF")
        print("3. Put all PDFs in a folder called 'pdfs'")
        print("4. Run manual_pdf_analyzer.py to analyze them")
        
        # Save committee URLs for reference
        urls_file = f'committee_urls_{timestamp}.txt'
        with open(urls_file, 'w') as f:
            f.write("DeKalb County Committee URLs\n")
            f.write("Open these in your browser to download PDFs manually:\n")
            f.write("=" * 60 + "\n\n")
            
            for committee_name, urls in committees.items():
                f.write(f"{committee_name}:\n")
                f.write(f"  Main: {urls['main']}\n")
                f.write(f"  Archive: {urls['archive']}\n\n")
        
        print(f"\nCommittee URLs saved to: {urls_file}")

if __name__ == "__main__":
    get_pdf_urls()