import re
import requests
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter

_START_MARKER = re.compile(r"Press Releases\s*\(\s*\d+\s*kb\s*\)\s*Date\s*:\s*[A-Za-z]+\s+\d{1,2},\s*\d{4}")
_CALENDAR_MARKER = re.compile(r"January\s+February\s+March\s+April\s+May\s+June\s+July\s+August\s+September\s+October\s+November\s+December", re.I)
_FOOTER_MARKERS = [
    re.compile(r"YouTube Instagram Facebook", re.I),
    re.compile(r"Sitemap\s*\|\s*Disclaimer", re.I),
]

def clean_content(raw_text):
    """Strip RBI site navigation, calendar, and footer boilerplate."""
    if not raw_text:
        return raw_text
    start_matches = list(_START_MARKER.finditer(raw_text))
    start_idx = start_matches[-1].end() if start_matches else 0
    end_idx = len(raw_text)
    cal_match = _CALENDAR_MARKER.search(raw_text, pos=start_idx)
    if cal_match:
        end_idx = min(end_idx, cal_match.start())
    for pattern in _FOOTER_MARKERS:
        match = pattern.search(raw_text, pos=start_idx)
        if match:
            end_idx = min(end_idx, match.start())
    cleaned = raw_text[start_idx:end_idx].strip()
    return cleaned if len(cleaned) >= 50 else raw_text.strip()

def is_boilerplate_chunk(chunk_text):
    if _CALENDAR_MARKER.search(chunk_text):
        return True
    if re.search(r"Skip to main content", chunk_text, re.I):
        return True
    return any(pattern.search(chunk_text) for pattern in _FOOTER_MARKERS)

def scrape_content(url):
    """Fetch and clean text from an RBI regulatory page."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return clean_content(soup.get_text(separator=' ', strip=True))
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return ""

def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return [chunk for chunk in splitter.split_text(text) if not is_boilerplate_chunk(chunk)]
