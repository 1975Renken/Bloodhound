#!/usr/bin/env python3
"""
Manual PDF Analyzer for DeKalb County Meeting Minutes
Use this when the website blocks automated access
"""

import os
import re
import PyPDF2
import pandas as pd
from datetime import datetime
from typing import List, Dict, Tuple
import json

class ManualPDFAnalyzer:
    """Analyze PDFs that you've manually downloaded"""
    
    def __init__(self):
        """Initialize the analyzer"""
        
        # Keywords by priority
        self.keywords = {
            'priority_1': [
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
            'priority_2': [
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
            'priority_3': [
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
            'priority_4': [
                r'\btraining\s+budget\b',
                r'\bprofessional\s+development\b',
                r'\bmandatory\s+training\b',
                r'\bcompliance\s+training\b',
                r'\bharassment\s+training\b',
                r'\bdiscrimination\b',
                r'\bhostile\s+work\s+environment\b'
            ]
        }
        
        self.results = []
        
    def extract_text_from_pdf(self, pdf_path: str) -> List[Tuple[int, str]]:
        """Extract text from a PDF file"""
        text_pages = []
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                print(f"  Processing {len(reader.pages)} pages...")
                
                for i, page in enumerate(reader.pages, 1):
                    try:
                        text = page.extract_text()
                        if text and len(text.strip()) > 50:
                            text_pages.append((i, text))
                    except:
                        print(f"    Warning: Could not extract text from page {i}")
                        
        except Exception as e:
            print(f"  Error reading PDF: {e}")
        
        return text_pages
    
    def search_keywords_in_text(self, text: str, page_num: int, pdf_name: str) -> List[Dict]:
        """Search for keywords in text"""
        matches = []
        
        for priority, patterns in self.keywords.items():
            for pattern in patterns:
                # Search with regex
                for match in re.finditer(pattern, text, re.IGNORECASE | re.DOTALL):
                    # Get context
                    start = max(0, match.start() - 300)
                    end = min(len(text), match.end() + 300)
                    context = text[start:end].strip()
                    context = ' '.join(context.split())  # Clean whitespace
                    
                    matches.append({
                        'pdf_filename': pdf_name,
                        'page': page_num,
                        'priority': priority,
                        'keyword': pattern,
                        'matched_text': match.group(),
                        'context': context
                    })
        
        return matches
    
    def analyze_pdf(self, pdf_path: str) -> int:
        """Analyze a single PDF file"""
        pdf_name = os.path.basename(pdf_path)
        print(f"\nAnalyzing: {pdf_name}")
        
        # Extract text
        text_pages = self.extract_text_from_pdf(pdf_path)
        
        if not text_pages:
            print("  No text could be extracted (might be scanned/image PDF)")
            return 0
        
        # Search for keywords
        total_matches = 0
        for page_num, text in text_pages:
            matches = self.search_keywords_in_text(text, page_num, pdf_name)
            self.results.extend(matches)
            total_matches += len(matches)
        
        print(f"  Found {total_matches} keyword matches")
        return total_matches
    
    def analyze_folder(self, folder_path: str):
        """Analyze all PDFs in a folder"""
        if not os.path.exists(folder_path):
            print(f"Error: Folder '{folder_path}' does not exist")
            return
        
        # Find all PDF files
        pdf_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
        
        if not pdf_files:
            print(f"No PDF files found in '{folder_path}'")
            return
        
        print(f"Found {len(pdf_files)} PDF files to analyze")
        print("=" * 60)
        
        # Analyze each PDF
        total_findings = 0
        for pdf_path in pdf_files:
            findings = self.analyze_pdf(pdf_path)
            total_findings += findings
        
        print("\n" + "=" * 60)
        print(f"ANALYSIS COMPLETE")
        print(f"Total PDFs analyzed: {len(pdf_files)}")
        print(f"Total findings: {total_findings}")
        
    def generate_reports(self):
        """Generate Excel and text reports"""
        if not self.results:
            print("\nNo findings to report")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create DataFrame
        df = pd.DataFrame(self.results)
        
        # Save Excel report
        excel_file = f'manual_analysis_{timestamp}.xlsx'
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # All findings
            df.to_excel(writer, sheet_name='All Findings', index=False)
            
            # Summary by priority
            priority_summary = df.groupby('priority').size().reset_index(name='count')
            priority_summary.to_excel(writer, sheet_name='Priority Summary', index=False)
            
            # Summary by PDF
            pdf_summary = df.groupby('pdf_filename').size().reset_index(name='findings')
            pdf_summary.to_excel(writer, sheet_name='PDF Summary', index=False)
        
        print(f"\n✓ Excel report saved: {excel_file}")
        
        # Save JSON for further processing
        json_file = f'manual_analysis_{timestamp}.json'
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"✓ JSON data saved: {json_file}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("FINDINGS SUMMARY")
        print("=" * 60)
        
        # Group by priority
        for priority in ['priority_1', 'priority_2', 'priority_3', 'priority_4']:
            priority_results = [r for r in self.results if r['priority'] == priority]
            if priority_results:
                print(f"\n{priority.upper()} ({len(priority_results)} findings):")
                # Show first 3 examples
                for i, result in enumerate(priority_results[:3], 1):
                    print(f"  {i}. PDF: {result['pdf_filename']}")
                    print(f"     Page: {result['page']}")
                    print(f"     Match: '{result['matched_text']}'")
                    print(f"     Context: ...{result['context'][:150]}...")
                if len(priority_results) > 3:
                    print(f"  ... and {len(priority_results) - 3} more")
        
        # Show high-priority findings in detail
        priority_1 = [r for r in self.results if r['priority'] == 'priority_1']
        if priority_1:
            print("\n" + "=" * 60)
            print("HIGH PRIORITY FINDINGS (PRIORITY 1) - DETAILED")
            print("=" * 60)
            for i, result in enumerate(priority_1, 1):
                print(f"\nFinding #{i}:")
                print(f"PDF: {result['pdf_filename']}")
                print(f"Page: {result['page']}")
                print(f"Keyword Pattern: {result['keyword']}")
                print(f"Matched Text: '{result['matched_text']}'")
                print(f"Full Context:")
                print(f"  {result['context']}")
                print("-" * 40)


def main():
    """Main entry point"""
    print("=" * 60)
    print("DEKALB COUNTY MANUAL PDF ANALYZER")
    print("=" * 60)
    print("\nThis tool analyzes PDFs you've manually downloaded.")
    print("It searches for keywords related to governance issues.\n")
    
    # Ask user for folder path
    print("Enter the path to the folder containing your PDFs:")
    print("(or press Enter to use 'pdfs' folder in current directory)")
    
    folder_path = input("> ").strip()
    if not folder_path:
        folder_path = "pdfs"
    
    # Create analyzer
    analyzer = ManualPDFAnalyzer()
    
    # Analyze folder
    analyzer.analyze_folder(folder_path)
    
    # Generate reports
    analyzer.generate_reports()
    
    print("\n" + "=" * 60)
    print("Analysis complete! Check the generated files:")
    print("- Excel report with all findings")
    print("- JSON file with raw data")
    print("=" * 60)


if __name__ == "__main__":
    main()