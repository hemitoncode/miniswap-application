import requests
import time
from urllib.parse import quote
from bs4 import BeautifulSoup
from .normalizer import normalizeName
from .config import *
import certifi

def searchBuildInstructions(kitName):
    """
    SEARCH BUILD INSTRUCTIONS ANNOTATIONS:
    Search for build instructions for a given kit name.
    
    Fetches search results from the configured search URL, extracts article titles
    and links, and returns them as a list of dictionaries. Includes retry logic
    for handling network failures.
    """
    # Normalize and URL-encode the kit name for the search query
    query = quote(normalizeName(kitName))
    url = f"{SEARCH_URL}{query}"
    
    # Retry logic: attempt up to MAX_RETRIES times with delays between requests
    for attempt in range(1, MAX_RETRIES + 1):
        time.sleep(DELAY_BETWEEN_REQUESTS)
        try:
            response = requests.get(url, headers=HEADERS, timeout=15, verify=certifi.where())
            if response.status_code == 200:
                break  # Success - exit retry loop
            else:
                print(f"Attempt {attempt}: HTTP {response.status_code} for {kitName}")
        except requests.RequestException as e:
            print(f"Attempt {attempt} error for {kitName}: {e}")
    else:
        # All retries exhausted without success
        print(f"Failed to fetch search page for {kitName} after {MAX_RETRIES} attempts")
        return []
    
    # Parse the HTML response
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    
    # Extract title and URL from each article element in the search results
    for article in soup.select("article"):
        titleEl = article.find("h2")
        linkEl = article.find("a")
        
        # Skip articles missing required elements
        if not titleEl or not linkEl:
            continue
        
        # Store cleaned title text and URL
        results.append({
            "title": titleEl.get_text(strip=True),
            "url": linkEl["href"]
        })
    
    return results
