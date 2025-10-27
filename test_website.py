#!/usr/bin/env python3
"""
Test script to check DeKalb County website structure
"""

import requests
from bs4 import BeautifulSoup
import json

def test_website():
    url = 'https://dekalbcounty.org/government/county-boards-commissions/finance/'
    
    print(f"Testing URL: {url}")
    print("=" * 60)
    
    # Try different user agents and headers
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    for i, user_agent in enumerate(user_agents, 1):
        print(f"\n--- Attempt {i} with User-Agent: {user_agent[:50]}... ---")
        
        try:
            headers = {
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            print(f"Status Code: {response.status_code}")
            print(f"Content Type: {response.headers.get('content-type', 'Unknown')}")
            print(f"Content Length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                print("SUCCESS! Website accessible with this User-Agent")
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all links
                all_links = soup.find_all('a', href=True)
                print(f"\nTotal links found: {len(all_links)}")
                
                # Look for PDF links specifically
                pdf_links = []
                for link in all_links:
                    href = link.get('href', '')
                    if '.pdf' in href.lower():
                        pdf_links.append({
                            'text': link.get_text(strip=True),
                            'href': href,
                            'full_url': requests.compat.urljoin(url, href)
                        })
                
                print(f"\nPDF links found: {len(pdf_links)}")
                for link in pdf_links:
                    print(f"  - {link['text']} -> {link['href']}")
                
                # Look for any links that might contain meeting materials
                meeting_links = []
                for link in all_links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True).lower()
                    if any(word in text for word in ['meeting', 'agenda', 'minutes', 'packet', 'audio']):
                        meeting_links.append({
                            'text': link.get_text(strip=True),
                            'href': href,
                            'full_url': requests.compat.urljoin(url, href)
                        })
                
                print(f"\nMeeting-related links found: {len(meeting_links)}")
                for link in meeting_links[:10]:  # Show first 10
                    print(f"  - {link['text']} -> {link['href']}")
                
                # Check for iframes or embedded content
                iframes = soup.find_all('iframe')
                print(f"\nIframes found: {len(iframes)}")
                for iframe in iframes:
                    src = iframe.get('src', '')
                    print(f"  - {src}")
                
                # Check for JavaScript that might load content
                scripts = soup.find_all('script')
                print(f"\nScripts found: {len(scripts)}")
                
                # Look for table structures
                tables = soup.find_all('table')
                print(f"\nTables found: {len(tables)}")
                for i, table in enumerate(tables):
                    print(f"  Table {i+1}: {len(table.find_all('tr'))} rows")
                    # Show first few rows
                    rows = table.find_all('tr')[:3]
                    for row in rows:
                        cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                        print(f"    {' | '.join(cells)}")
                
                break  # Success, no need to try other user agents
                
            elif response.status_code == 403:
                print("403 Forbidden - Website blocking access")
                # Show what the 403 response contains
                soup = BeautifulSoup(response.content, 'html.parser')
                title = soup.find('title')
                if title:
                    print(f"Page title: {title.get_text()}")
                
                # Look for any error messages
                error_msgs = soup.find_all(['h1', 'h2', 'h3', 'p'])
                for msg in error_msgs[:5]:
                    text = msg.get_text(strip=True)
                    if text and len(text) > 10:
                        print(f"Content: {text}")
                
            else:
                print(f"Failed to access website. Status: {response.status_code}")
                
        except Exception as e:
            print(f"Error: {e}")
    
    # If all attempts failed, suggest alternatives
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS:")
    print("1. The website is blocking automated access (403 Forbidden)")
    print("2. Try using a different network/VPN")
    print("3. Use browser automation (Selenium)")
    print("4. Download PDFs manually and process them locally")
    print("5. Check if the website has changed its structure")

if __name__ == "__main__":
    test_website() 