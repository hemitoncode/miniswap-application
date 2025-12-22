from config import *
from bs4 import BeautifulSoup
import requests
import time
import certifi

def getPdfLink(pageUrl):
    """
    Extract the first PDF link from a candidate page.
    
    Fetches the page content, parses it for anchor tags, and returns the first
    link that ends with .pdf. Includes retry logic for network failures. This is
    useful when the page itself isn't the PDF, but contains a link to download it.
    """
    # Retry logic: we may encounter temporary network issues or rate limiting,
    # so we attempt multiple times before giving up
    for attempt in range(1, MAX_RETRIES + 1):
        # Delay between requests to be respectful to the server and avoid rate limiting
        time.sleep(DELAY_BETWEEN_REQUESTS)
        try:
            # Fetch the candidate page with SSL verification using certifi certificates
            response = requests.get(pageUrl, headers=HEADERS, timeout=15, verify=certifi.where())
            
            # If we didn't get a successful response, try again on next iteration
            # Don't return here so we can retry with the same URL
            if response.status_code != 200:
                continue
            
            # Parse the HTML to search for links
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Iterate through all anchor tags that have an href attribute
            # We're looking for any direct PDF links on this page
            for a in soup.find_all("a", href=True):
                href = a["href"]
                
                # Case-insensitive check for .pdf extension
                # This catches .PDF, .pdf, .Pdf, etc.
                if href.lower().endswith(".pdf"):
                    return href  # Return immediately on first PDF found
            
            # We successfully fetched the page but found no PDFs
            # No point retrying, so return None
            return None
        
        except requests.RequestException as e:
            # Network error occurred - log it and try again if retries remain
            print(f"Attempt {attempt} error fetching candidate page {pageUrl}: {e}")
    
    # All retries exhausted without finding a PDF or successful page fetch
    return None

def downloadPdf(pdfUrl, filename):
    """
    Download a PDF file from a given URL and save it locally.
    
    Attempts to download the PDF with retry logic to handle transient failures.
    Saves the binary content to the specified filename. Returns True if successful,
    False if all retry attempts fail.
    """
    # Retry logic: PDF downloads can fail due to network issues, timeouts, or server problems
    # Multiple attempts increase our chances of success
    for attempt in range(1, MAX_RETRIES + 1):
        # Delay between requests to avoid overwhelming the server
        time.sleep(DELAY_BETWEEN_REQUESTS)
        try:
            # Fetch the PDF content directly from the URL
            # Using SSL verification to ensure we're connecting to the legitimate server
            response = requests.get(pdfUrl, headers=HEADERS, timeout=15, verify=certifi.where())
            
            if response.status_code == 200:
                # Successful download - write the binary content to disk
                # Using 'wb' mode for binary write since PDFs are binary files
                with open(filename, "wb") as f:
                    f.write(response.content)
                print(f"Downloaded PDF: {filename}")
                return True  # Success - no need to retry
            else:
                # Non-200 status code - could be 404, 403, 500, etc.
                # Log it and try again in case it's a temporary server issue
                print(f"Attempt {attempt}: HTTP {response.status_code} for {pdfUrl}")
        
        except requests.RequestException as e:
            # Network error (timeout, connection refused, DNS failure, etc.)
            # Log the error and continue to next retry attempt
            print(f"Attempt {attempt} error downloading {pdfUrl}: {e}")
    
    # All retry attempts exhausted without successful download
    # Log final failure message and return False to indicate failure
    print(f"Failed to download PDF after {MAX_RETRIES} attempts: {pdfUrl}")
    return False
