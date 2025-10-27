#!/usr/bin/env python3
"""
DeKalb County Meeting Minutes PDF Mining Tool - Fixed Version
Includes anti-bot detection bypass techniques
"""

import os
import re
import csv
import json
import time
import logging
import random
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import PyPDF2
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    print("Warning: pdfplumber not installed, using PyPDF2 only")

import pandas as pd
from collections import defaultdict
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_miner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DeKalbPDFMiner:
    """Main class for mining DeKalb County meeting minutes PDFs"""
    
    def __init__(self, base_dir: str = "dekalb_pdfs"):
        """Initialize the PDF miner with configuration"""
        self.base_dir = base_dir
        
        # Create session with browser-like headers
        self.session = requests.Session()
        
        # Rotate user agents to appear more natural
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]
        
        # Set comprehensive headers to bypass bot detection
        self.update_headers()
        
        # Committee information
        self.committees = {
            'finance_administration': {
                'name': 'Finance & Administration',
                'main_url': 'https://dekalbcounty.org/government/county-boards-commissions/finance/',
                'archive_url': 'https://dekalbcounty.org/government/county-boards-commissions/finance/finance-committee-archive/'
            },
            'highway': {
                'name': 'Highway',
                'main_url': 'https://dekalbcounty.org/government/county-boards-commissions/county-highway/',
                'archive_url': 'https://dekalbcounty.org/government/county-boards-commissions/county-highway/highway-committee-archive/'
            },
            'law_justice': {
                'name': 'Law & Justice',
                'main_url': 'https://dekalbcounty.org/government/county-boards-commissions/law-justice/',
                'archive_url': 'https://dekalbcounty.org/government/county-boards-commissions/law-justice/law-justice-archive/'
            },
            'committee_whole': {
                'name': 'Committee of the Whole',
                'main_url': 'https://dekalbcounty.org/government/county-boards-commissions/committee-of-the-whole/',
                'archive_url': 'https://dekalbcounty.org/government/county-boards-commissions/committee-of-the-whole/committee-of-the-whole-archive/'
            },
            'executive': {
                'name': 'Executive',
                'main_url': 'https://dekalbcounty.org/government/county-boards-commissions/executive/',
                'archive_url': 'https://dekalbcounty.org/government/county-boards-commissions/executive/executive-committee-archive/'
            },
            'county_board': {
                'name': 'County Board',
                'main_url': 'https://dekalbcounty.org/government/county-boards-commissions/county-board-meetings/',
                'archive_url': 'https://dekalbcounty.org/government/county-boards-commissions/county-board-meetings/county-board-archives/'
            },
            'board_review': {
                'name': 'Board of Review',
                'main_url': 'https://dekalbcounty.org/departments/assessment-office/board-of-review/board-of-review-meetings/',
                'archive_url': 'https://dekalbcounty.org/departments/assessment-office/board-of-review/board-of-review-meetings/board-of-review-archives/'
            }
        }
        
        # Keywords by priority
        self.keywords = {
            'priority_1': {
                'terms': [
                    r'\bSteve\s+Hamm\b', r'\bS\.\s*Hamm\b', r'\bHamm\b',
                    r'\bethics\s+training\b',
                    r'\babuse\s+of\s+(authority|position)\b',
                    r'\bconflict\s+of\s+interest\b',
                    r'\bemployee\s+misconduct\b',
                    r'\bhighway\s+department\b.*?\b(complaint|incident|investigation)\b',
                    r'\bG-K\s+Broncos\b', r'\bBroncos\b',
                    r'\bKingston\s+Park\b',
                    r'\btrailer\s+removal\b'
                ],
                'color': 'FF0000'  # Red
            },
            'priority_2': {
                'terms': [
                    r'\bethics\b.*?\b(training|policy|violation)\b',
                    r'\bcode\s+of\s+conduct\b',
                    r'\bemployee\s+handbook\b',
                    r'\bdisciplinary\s+action\b',
                    r'\b(grievance|complaint)\b',
                    r'\binappropriate\s+use\b',
                    r'\bpersonal\s+use\b.*?\b(vehicle|position|authority)\b',
                    r'\bsheriff\b.*?\bhighway\b',
                    r'\b(intimidation|threatening)\b',
                    r'\bretaliation\b'
                ],
                'color': 'FFA500'  # Orange
            },
            'priority_3': {
                'terms': [
                    r'\boversight\b',
                    r'\baccountability\b',
                    r'\binternal\s+investigation\b',
                    r'\boutside\s+counsel\b',
                    r'\blitigation\s+hold\b',
                    r'\b(lawsuit|legal\s+action)\b',
                    r'\bsettlement\b',
                    r'\binsurance\s+claim\b',
                    r'\b(FOIA|freedom\s+of\s+information)\b',
                    r'\bpublic\s+comment\b.*?\b(complaint|concern)\b'
                ],
                'color': 'FFFF00'  # Yellow
            },
            'priority_4': {
                'terms': [
                    r'\btraining\s+budget\b',
                    r'\bprofessional\s+development\b',
                    r'\bmandatory\s+training\b',
                    r'\bcompliance\s+training\b',
                    r'\bharassment\s+training\b',
                    r'\bdiscrimination\b',
                    r'\bhostile\s+work\s+environment\b'
                ],
                'color': '00FF00'  # Green
            }
        }
        
        # Initialize results storage
        self.results = []
        self.pdf_cache = {}
        
    def update_headers(self):
        """Update session headers with a random user agent"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.google.com/'
        }
        self.session.headers.update(headers)
        
    def setup_directories(self):
        """Create directory structure for storing PDFs"""
        for committee_key in self.committees:
            committee_dir = os.path.join(self.base_dir, committee_key)
            os.makedirs(committee_dir, exist_ok=True)
            os.makedirs(os.path.join(committee_dir, 'current'), exist_ok=True)
            os.makedirs(os.path.join(committee_dir, 'archive'), exist_ok=True)
        
        # Create results directory
        os.makedirs('results', exist_ok=True)
        logger.info(f"Directory structure created under {self.base_dir}")
    
    def get_page_with_retry(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Get a webpage with retry logic and anti-bot measures"""
        for attempt in range(max_retries):
            try:
                # Random delay to appear more human
                time.sleep(random.uniform(2, 5))
                
                # Update headers for each request
                self.update_headers()
                
                # Make request
                response = self.session.get(url, timeout=30, allow_redirects=True)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 403:
                    logger.warning(f"403 Forbidden on attempt {attempt + 1} for {url}")
                    if attempt < max_retries - 1:
                        # Longer wait before retry
                        wait_time = random.uniform(10, 20)
                        logger.info(f"Waiting {wait_time:.1f} seconds before retry...")
                        time.sleep(wait_time)
                        # Clear cookies and try fresh session
                        self.session.cookies.clear()
                    continue
                else:
                    response.raise_for_status()
                    
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1} for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(5, 10))
                    
        return None
    
    def extract_pdf_links(self, url: str) -> List[Dict]:
        """Extract all PDF links from a webpage"""
        pdf_links = []
        
        response = self.get_page_with_retry(url)
        if not response:
            logger.error(f"Failed to access {url} after retries")
            return pdf_links
            
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links to PDFs
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.lower().endswith('.pdf'):
                    full_url = urljoin(url, href)
                    link_text = link.get_text(strip=True)
                    
                    # Try to extract date from filename or link text
                    date_match = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})|(\w+\s+\d{1,2},?\s+\d{4})', link_text + ' ' + href)
                    date_str = date_match.group() if date_match else 'Unknown'
                    
                    pdf_links.append({
                        'url': full_url,
                        'text': link_text,
                        'date_str': date_str,
                        'filename': os.path.basename(urlparse(full_url).path)
                    })
            
            logger.info(f"Found {len(pdf_links)} PDFs on {url}")
        except Exception as e:
            logger.error(f"Error parsing PDFs from {url}: {e}")
        
        return pdf_links
    
    def download_pdf(self, pdf_info: Dict, save_path: str) -> bool:
        """Download a single PDF file"""
        try:
            # Check if already downloaded
            if os.path.exists(save_path):
                logger.info(f"PDF already exists: {save_path}")
                return True
            
            # Random delay
            time.sleep(random.uniform(1, 3))
            
            # Update headers
            self.update_headers()
            
            response = self.session.get(pdf_info['url'], timeout=60, stream=True)
            response.raise_for_status()
            
            # Save PDF
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded: {pdf_info['filename']}")
            return True
        except Exception as e:
            logger.error(f"Error downloading {pdf_info['url']}: {e}")
            return False
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Tuple[int, str]]:
        """Extract text from PDF, returns list of (page_num, text) tuples"""
        text_pages = []
        
        try:
            # Try with pdfplumber first if available
            if HAS_PDFPLUMBER:
                try:
                    with pdfplumber.open(pdf_path) as pdf:
                        for i, page in enumerate(pdf.pages, 1):
                            text = page.extract_text()
                            if text and len(text.strip()) > 50:
                                text_pages.append((i, text))
                except:
                    pass
                        
            # If no text extracted or pdfplumber not available, try PyPDF2
            if not text_pages:
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for i, page in enumerate(reader.pages, 1):
                        text = page.extract_text()
                        if text and len(text.strip()) > 50:
                            text_pages.append((i, text))
                
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
        
        return text_pages
    
    def search_keywords_in_text(self, text: str, page_num: int, pdf_info: Dict, committee: str) -> List[Dict]:
        """Search for keywords in text and return matches with context"""
        matches = []
        text_lower = text.lower()
        
        for priority, priority_data in self.keywords.items():
            for pattern in priority_data['terms']:
                # Search with regex (case-insensitive)
                for match in re.finditer(pattern, text, re.IGNORECASE | re.DOTALL):
                    # Get context (50 words before and after)
                    start = max(0, match.start() - 300)
                    end = min(len(text), match.end() + 300)
                    context = text[start:end].strip()
                    
                    # Clean up context
                    context = ' '.join(context.split())
                    
                    matches.append({
                        'committee': committee,
                        'pdf_filename': pdf_info['filename'],
                        'pdf_date': pdf_info['date_str'],
                        'page': page_num,
                        'priority': priority,
                        'keyword_pattern': pattern,
                        'matched_text': match.group(),
                        'context': context,
                        'url': pdf_info['url']
                    })
        
        return matches
    
    def process_committee(self, committee_key: str):
        """Process all PDFs for a single committee"""
        committee = self.committees[committee_key]
        committee_name = committee['name']
        logger.info(f"\nProcessing {committee_name}...")
        
        # Get PDFs from main page
        current_pdfs = self.extract_pdf_links(committee['main_url'])
        
        # Get PDFs from archive page
        archive_pdfs = self.extract_pdf_links(committee['archive_url'])
        
        # Download and process current PDFs
        for pdf_info in tqdm(current_pdfs, desc=f"{committee_name} - Current"):
            save_path = os.path.join(self.base_dir, committee_key, 'current', pdf_info['filename'])
            if self.download_pdf(pdf_info, save_path):
                # Extract and search text
                text_pages = self.extract_text_from_pdf(save_path)
                for page_num, text in text_pages:
                    matches = self.search_keywords_in_text(text, page_num, pdf_info, committee_name)
                    self.results.extend(matches)
        
        # Download and process archive PDFs
        for pdf_info in tqdm(archive_pdfs, desc=f"{committee_name} - Archive"):
            save_path = os.path.join(self.base_dir, committee_key, 'archive', pdf_info['filename'])
            if self.download_pdf(pdf_info, save_path):
                # Extract and search text
                text_pages = self.extract_text_from_pdf(save_path)
                for page_num, text in text_pages:
                    matches = self.search_keywords_in_text(text, page_num, pdf_info, committee_name)
                    self.results.extend(matches)
    
    def generate_excel_report(self):
        """Generate comprehensive Excel report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        excel_path = f'results/dekalb_findings_{timestamp}.xlsx'
        
        # Create DataFrame from results
        df = pd.DataFrame(self.results)
        
        if df.empty:
            logger.warning("No results to report")
            return None
        
        # Save to Excel
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='All Findings', index=False)
            
            # Add summary sheets if we have data
            if not df.empty:
                # Committee summary
                committee_summary = df.groupby(['committee', 'priority']).size().unstack(fill_value=0)
                committee_summary.to_excel(writer, sheet_name='Committee Summary')
                
                # Priority summary
                priority_summary = df.groupby(['priority', 'committee']).size().unstack(fill_value=0)
                priority_summary.to_excel(writer, sheet_name='Priority Summary')
        
        logger.info(f"Excel report generated: {excel_path}")
        return excel_path
    
    def generate_summary_report(self):
        """Generate a text summary report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_path = f'results/dekalb_summary_{timestamp}.txt'
        
        with open(summary_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("DEKALB COUNTY MEETING MINUTES ANALYSIS SUMMARY\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            if not self.results:
                f.write("No findings identified in the analyzed documents.\n")
                f.write("\nPossible reasons:\n")
                f.write("- Website may be blocking automated access (403 errors)\n")
                f.write("- PDFs may be scanned images requiring OCR\n")
                f.write("- Keywords may not appear in the documents\n")
                f.write("\nTroubleshooting:\n")
                f.write("1. Try accessing the URLs manually in a browser\n")
                f.write("2. Download a few PDFs manually and test with those\n")
                f.write("3. Check if the website requires authentication\n")
                return summary_path
            
            df = pd.DataFrame(self.results)
            
            # Overall statistics
            f.write("OVERALL STATISTICS\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total findings: {len(df)}\n")
            f.write(f"Committees analyzed: {df['committee'].nunique()}\n")
            f.write(f"PDFs processed: {df['pdf_filename'].nunique()}\n")
            f.write(f"Unique keywords matched: {df['keyword_pattern'].nunique()}\n\n")
            
            # Priority breakdown
            f.write("FINDINGS BY PRIORITY\n")
            f.write("-" * 40 + "\n")
            for priority in ['priority_1', 'priority_2', 'priority_3', 'priority_4']:
                count = len(df[df['priority'] == priority])
                if len(df) > 0:
                    percentage = (count / len(df)) * 100
                    f.write(f"{priority}: {count} ({percentage:.1f}%)\n")
            
        logger.info(f"Summary report generated: {summary_path}")
        return summary_path
    
    def run(self):
        """Main execution method"""
        logger.info("Starting DeKalb County PDF Mining Tool")
        logger.info("=" * 60)
        
        # Setup
        self.setup_directories()
        
        # Process each committee
        for committee_key in self.committees:
            self.process_committee(committee_key)
            # Longer random delay between committees
            time.sleep(random.uniform(5, 10))
        
        # Generate reports
        logger.info("\nGenerating reports...")
        excel_report = self.generate_excel_report()
        summary_report = self.generate_summary_report()
        
        # Final summary
        logger.info("\n" + "=" * 60)
        logger.info("MINING COMPLETE")
        logger.info(f"Total findings: {len(self.results)}")
        logger.info(f"Reports generated:")
        if excel_report:
            logger.info(f"  - Excel: {excel_report}")
        logger.info(f"  - Summary: {summary_report}")
        logger.info("=" * 60)
        
        return {
            'total_findings': len(self.results),
            'excel_report': excel_report,
            'summary_report': summary_report,
            'results': self.results
        }


def main():
    """Main entry point"""
    miner = DeKalbPDFMiner()
    results = miner.run()
    
    # Print quick summary to console
    print("\n" + "=" * 60)
    print("DEKALB COUNTY PDF MINING COMPLETE")
    print("=" * 60)
    print(f"Total findings: {results['total_findings']}")
    
    if results['total_findings'] > 0:
        df = pd.DataFrame(results['results'])
        print("\nTop findings by priority:")
        for priority in ['priority_1', 'priority_2', 'priority_3', 'priority_4']:
            count = len(df[df['priority'] == priority])
            if count > 0:
                print(f"  {priority}: {count} findings")
        
        print("\nReports saved to 'results' folder")
        print("Check the Excel file for detailed findings and context")
    else:
        print("\nNo keyword matches found.")
        print("\nIf you encountered 403 errors, try:")
        print("1. Running the manual_download.py script instead")
        print("2. Downloading PDFs manually through your browser")
        print("3. Using a VPN or different network connection")
    
    return results


if __name__ == "__main__":
    main()