import httpx
import re
from typing import Optional
from bs4 import BeautifulSoup
from readability import Document

# SEC.gov requires a specific User-Agent
DEFAULT_USER_AGENT = "StockPlanner/1.0 (contact@stockplanner.com)"

async def fetch_content(url: str, user_agent: str = DEFAULT_USER_AGENT) -> str:
    """
    Fetch HTML content from a URL with proper User-Agent.
    Returns empty string on failure.
    """
    if not url:
        return ""
        
    headers = {
        "User-Agent": user_agent
    }
    
    try:
        async with httpx.AsyncClient(headers=headers, timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url)
            
            if response.status_code >= 400:
                print(f"Error fetching {url}: {response.status_code}")
                return ""
                
            return response.text
    except Exception as e:
        print(f"Exception fetching {url}: {e}")
        return ""

def clean_html(html: str) -> str:
    """
    Extract core content from HTML using readability-lxml and BeautifulSoup.
    """
    if not html:
        return ""
        
    try:
        # 1. Clean boilerplate with readability
        clean_html_text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', html)
        doc = Document(clean_html_text)
        summary_html = doc.summary()
        
        # 2. Parse with BeautifulSoup to get clean text
        soup = BeautifulSoup(summary_html, 'lxml')
        text = soup.get_text(separator=' ', strip=True)
        
        if text:
            text = str(text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        return ""
    except Exception as e:
        print(f"Error cleaning HTML: {e}")
        return ""
