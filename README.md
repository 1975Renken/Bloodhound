# 🔍 Bloodhound

**PDF Keyword Search & Context Extraction Tool**

> *Sniff out key search terms across a database of PDFs and produce a spreadsheet with context showing where each term appears.*

---

## Overview

Bloodhound is a Python-based document analysis tool that searches through large collections of PDF files for specific keywords and patterns, extracting surrounding context to help researchers quickly identify relevant information.

**Key Features:**
- 📄 Batch PDF processing (handles hundreds of documents)
- 🔍 Regex-based keyword matching with multiple patterns
- 📊 Priority-based categorization system
- 📈 Excel report generation with multiple analysis sheets
- 🎯 Context extraction (captures surrounding text for each match)
- 📋 Comprehensive logging and error handling

---

## Real-World Use Case

Originally developed to analyze government meeting minutes for accountability research, Bloodhound successfully processed **200+ PDF documents** from DeKalb County (Illinois) committee archives, identifying **5,598 keyword matches** across multiple priority levels.

**Results:**
- **95 Priority 1 matches** (highest importance)
- **3,454 Priority 2 matches** 
- **1,939 Priority 3 matches**
- **110 Priority 4 matches**

---

## Technical Stack

```
Python 3.8+
├── PDF Processing: PyPDF2, pdfplumber
├── Data Analysis: pandas, numpy
├── Reporting: openpyxl (Excel generation)
├── Pattern Matching: regex
└── Utilities: logging, tqdm
```

---

## How It Works

### 1. Input
- Point Bloodhound at a folder containing PDF files
- Define your keyword patterns using regex
- Configure priority levels for different search terms

### 2. Processing
```
For each PDF:
  → Extract text from all pages
  → Search for keyword patterns
  → Capture surrounding context (±300 characters)
  → Tag with priority level
  → Store results with metadata
```

### 3. Output
Excel spreadsheet with:
- All matches with full context
- PDF filename and page number
- Keyword pattern that matched
- Priority classification
- Source URL (if applicable)

---

## Project Structure

```
bloodhound/
├── tool.py                    # Main analysis engine (600+ lines)
├── manual_pdf_analyzer.py     # Standalone version for offline use
├── quick_start.py             # Quick testing script
├── requirements.txt           # Dependencies
├── README.md                  # This file
└── results/
    └── dekalb_findings_[timestamp].xlsx
```

---

## Usage

### Basic Usage
```bash
# Install dependencies
pip install -r requirements.txt

# Run on a folder of PDFs
python manual_pdf_analyzer.py
# Enter folder path when prompted
```

### Customizing Keywords
Edit the keyword dictionary in the script:

```python
self.keywords = {
    'priority_1': [
        r'\bYourKeyword\b',
        r'\bSpecific\s+Pattern\b',
        # Add your high-priority patterns
    ],
    'priority_2': [
        # Medium priority patterns
    ],
    # ... etc
}
```

---

## Key Features Demonstrated

### Software Engineering
✅ **Modular architecture** - Clean separation of concerns  
✅ **Error handling** - Graceful degradation when PDFs fail to parse  
✅ **Logging system** - Comprehensive audit trail of operations  
✅ **Type hints** - Modern Python practices  
✅ **Documentation** - Docstrings and inline comments  

### Data Engineering
✅ **ETL Pipeline** - Extract (PDF) → Transform (regex search) → Load (Excel)  
✅ **Batch processing** - Handles large document collections  
✅ **Data validation** - Text length checks, duplicate detection  
✅ **Multiple export formats** - Excel, JSON, text reports  

### Problem Solving
✅ **Adaptive approach** - Web scraping didn't work → manual download workflow  
✅ **Dual PDF extraction** - pdfplumber + PyPDF2 for better compatibility  
✅ **Context preservation** - Not just matches, but surrounding text  
✅ **Priority system** - Triage results by importance  

---

## Known Limitations & Future Improvements

### Current Limitations
- **Context extraction**: Currently ~10% of matches capture full context successfully
  - *Why*: Some PDFs have complex formatting, tables, or encoding issues
  - *Impact*: Match is still recorded, just without surrounding text
  - *Workaround*: Matched text is always captured, can manually review those PDFs

- **OCR support**: Limited handling of scanned/image-based PDFs
  - *Why*: OCR dependencies (Tesseract) not in minimal version
  - *Impact*: Text-only PDFs work great; scanned documents need pre-processing

- **Web scraping**: Original automated download feature had reliability issues
  - *Solution*: Pivoted to manual PDF download workflow (actually more reliable)

### Future Enhancements
- [ ] Improve context extraction rate to >90%
- [ ] Add full OCR support for scanned documents
- [ ] Implement parallel processing for faster batch operations
- [ ] Add GUI for non-technical users
- [ ] Export to additional formats (JSON, CSV, HTML reports)
- [ ] Add visualization dashboard for results

---

## Development Notes

### AI-Assisted Development
This project was developed with AI assistance (Claude/ChatGPT) for:
- Initial code structure and boilerplate
- Regex pattern optimization
- Error handling strategies
- Documentation templates

**Human contribution** (where the real work happens):
- Problem definition and requirements
- Architecture decisions
- Testing and validation with real data
- Debugging and troubleshooting
- Adapting when original approach (web scraping) didn't work
- Creating the priority classification system
- Real-world deployment and usage

> **Note:** Using AI tools for coding is now standard practice in professional development. What matters is whether the code works, is maintainable, and solves the problem - all of which Bloodhound accomplishes.

---

## Real-World Impact

**Time Saved:** Manually reviewing 200 PDFs would take ~100 hours. Bloodhound completed the analysis in ~3 hours, including setup time.

**Actionable Results:** Identified 95 high-priority items requiring immediate review, saving countless hours of manual document scanning.

**Reusability:** Framework is adaptable to any PDF keyword search use case:
- Legal document discovery
- Academic literature review
- Compliance monitoring
- Contract analysis
- Research data mining

---

## Technical Challenges Solved

### Challenge 1: PDF Format Variability
**Problem:** PDFs come in many formats (text-based, scanned, mixed)  
**Solution:** Dual extraction pipeline with fallback methods

### Challenge 2: Context Preservation
**Problem:** Need surrounding text, not just keyword matches  
**Solution:** Implemented sliding window context extraction (±300 chars)

### Challenge 3: Large-Scale Processing
**Problem:** Processing hundreds of multi-page PDFs efficiently  
**Solution:** Progress bars, logging, and error recovery to handle batch operations

### Challenge 4: Results Organization
**Problem:** 5,000+ matches is overwhelming without structure  
**Solution:** Priority classification system and multi-sheet Excel reports

---

## Performance Metrics

**Test Case:** DeKalb County Meeting Minutes Analysis
- **PDFs Processed:** 200+ documents
- **Total Pages:** 3,000+ pages analyzed  
- **Processing Time:** ~3 hours
- **Matches Found:** 5,598 keyword occurrences
- **Success Rate:** 100% on text extraction, ~10% on context extraction
- **Output Size:** 330KB Excel file with comprehensive data

---

## Use Cases

### Current
- Government transparency research
- Public accountability investigations
- Meeting minute analysis

### Potential
- **Legal:** Contract review, e-discovery, case law research
- **Academic:** Literature review automation, citation analysis
- **Corporate:** Compliance monitoring, policy review
- **Journalism:** Investigative document analysis
- **Research:** Large-scale document mining

---

## Installation

### Requirements
```
Python 3.8+
pandas
openpyxl
PyPDF2
tqdm
```

### Quick Install
```bash
pip install -r requirements.txt
```

### Optional (for OCR support)
```bash
pip install pytesseract pdfplumber pdf2image
# Also requires Tesseract OCR system install
```

---

## License

Developed for public interest research and transparency purposes.

---

## Credits

**Developed by:** Timothy Lamoureux  
**Purpose:** Government accountability research  
**Tech Stack:** Python, pandas, PyPDF2  
**Development Approach:** AI-assisted with human oversight and testing  

---

## Why "Bloodhound"?

Because like a bloodhound tracking a scent, this tool relentlessly searches through documents to find exactly what you're looking for - following the trail of keywords through hundreds of pages to uncover hidden information.

---

**Status:** ✅ Functional | 🧪 Tested on 200+ real-world documents | 📊 Production results generated

**Last Updated:** January 2025
