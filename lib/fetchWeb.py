import requests
import time

'''
LINKS ANNOTATION:

All 2024 kits can be found on this page. Each path segment serves as a specific filter:

- /sets/games-workshop/necromunda/ is the base path for Necromunda kits from Games Workshop
- /sort-new sorts kits by newest first
- /type-miniature filters to only show miniature kits since that is what Miniswap deals with
- /kind-not3d filters out 3D digital assets since Miniswap only deals with physical kits. 
  Furthermore, I will create ANOTHER program to find instruction manuals which cannot apply 
  to 3d printing stuffs.
- The /view-details gives us detailed list instead of gallery view which gives release date without
  having to request each individual kit page. This way, we do not have to make extra requests to the
  detailed page to get the release date for filtering purposes.
- /show-20 shows 20 kits per page to reduce the number of pages we have to iterate through.
- /page- is the pagination segment to get different pages of listings. I will be iterating through 
  multiple pages starting from page 25 to get all 2024 kits.
'''

BASE_KIT_LISTING = 'https://miniset.net/sets/games-workshop/sort-new/type-miniature/kind-not3d/view-details/show-20/page-'

# These are the ranges of page which contain 2024 kits
# This way we do not have to scrape all pages for this catalog
START_PAGE = 25
END_PAGE = 52

# HTTP headers to make requests appear browser-like (helps avoid blocks and SSL issues)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}


'''
HELPER FUNCTIONS ANNOTATION:

- Helper functions to fetch web pages
- fetchListings: Fetches HTML content of kit listings pages, iterating through multiple pages
  starting from START_PAGE and continuing for MAX_PAGES iterations.
- fetchKitDetails: Fetches detailed HTML content for a specific kit based on sku link which is 
  retrieved from parsing HTML of the kit listing page.
  
Both functions use a TWO-TIER RETRY STRATEGY to handle SSL certificate errors:
  TIER 1: Always attempt HTTPS request with SSL verification enabled (secure & proper)
  TIER 2: If SSL fails, retry WITHOUT verification (fallback for certificate issues)
  
This approach prioritizes security but ensures scraping continues even if miniset.net
has SSL certificate problems.
'''


def fetchListings():
    """
    FETCH LISTING ANNOTATION:

    Generator function that fetches kit listing pages sequentially.
    Starts at START_PAGE and fetches through END_PAGE.
    Yields HTML content for each successfully fetched page.
    
    RETRY LOGIC EXPLANATION:
    --------------------------------------------------
    The function uses a try-except structure with TWO attempts per page:
    
    ATTEMPT 1 (Secure Method):
        - Makes HTTPS request WITH SSL certificate verification
        - This is the PROPER way to make requests (secure & encrypted)
        - Will succeed if the website has valid SSL certificates
        
    ATTEMPT 2 (Fallback Method):
        - Only runs if ATTEMPT 1 throws an SSLError
        - Makes HTTPS request WITHOUT SSL certificate verification (verify=False)
        - This bypasses certificate validation completely
        - Less secure, but allows data collection to continue
        
    WHY THIS APPROACH?
        - Some websites have expired/misconfigured SSL certificates
        - Rather than failing completely, we attempt the insecure method as backup
        - The ⚠ warning symbol alerts us when the fallback is used
        - We can investigate SSL issues later without blocking our scraping work
    """
    for currentPage in range(START_PAGE, END_PAGE + 1):
        print(f"Fetching listings page: {currentPage}")
        kitListingsLink = f"{BASE_KIT_LISTING}{currentPage}"
        
        # Add delay between requests to be polite and avoid rate limiting
        time.sleep(0.5)
        
        try:
            # ATTEMPT 1: Secure method with SSL verification
            response = requests.get(kitListingsLink, headers=HEADERS, timeout=15)
            if response.status_code == 200:
                yield response.text
            else:
                print(f"  ✗ Failed to retrieve page {currentPage} - Status code: {response.status_code}")
                yield None
                
        except requests.exceptions.SSLError as ssl_error:
            # ATTEMPT 2: Fallback without SSL verification
            # Triggered when: SSL certificate is invalid, expired, or can't be verified
            print(f"  ⚠ SSL error on page {currentPage}, retrying without verification...")
            try:
                response = requests.get(kitListingsLink, headers=HEADERS, timeout=15, verify=False)
                if response.status_code == 200:
                    yield response.text
                else:
                    print(f"  ✗ Failed even without SSL verification - Status code: {response.status_code}")
                    yield None
            except requests.RequestException as e:
                print(f"  ✗ Error on retry: {e}")
                yield None
                
        except requests.RequestException as e:
            # Catches other network errors (timeout, connection refused, DNS failure, etc.)
            print(f"  ✗ Error fetching page {currentPage}: {e}")
            yield None


def fetchKitDetails(sku):
    """
    FETCH KIT DETAILS ANNOTATION:

    Fetches detailed HTML content for a specific kit.
    
    Args:
        sku: The SKU of the kit (e.g., "99123016002")
        
    Returns:
        HTML content as string if successful, None otherwise
        
    RETRY LOGIC EXPLANATION:
    --------------------------------------------------
    Uses the SAME two-tier retry strategy as fetchListings():
    
    ATTEMPT 1 (Secure):
        - HTTPS with SSL verification (verify=True by default)
        - Ensures encrypted connection with verified certificate
        
    ATTEMPT 2 (Fallback):
        - Only runs if SSLError is caught from ATTEMPT 1
        - HTTPS WITHOUT SSL verification (verify=False)
        - Also disables SSL warnings to keep console output clean
        
    WHEN ATTEMPT 2 RUNS:
        - SSL certificate can't be verified (expired, self-signed, wrong domain, etc.)
        - Connection still encrypted, but we can't verify server identity
        - Print statement shows "(without SSL verification)" so we know it happened
        
    WHY DISABLE WARNINGS?
        - When verify=False is used, urllib3 spams warnings to console
        - We already print our own warning message (⚠ symbol)
        - Disabling prevents duplicate/redundant warning spam
        - Makes output cleaner and easier to read
    """
    kitLink = f"https://miniset.net/sets/gw-{sku}"
    
    # Add small delay between requests to be polite and avoid rate limiting
    time.sleep(0.3)
    
    try:
        # ATTEMPT 1: Secure method with SSL verification
        response = requests.get(kitLink, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            print(f"  ✓ Fetched details for {sku}")
            return response.text
        else:
            print(f"  ✗ Failed to retrieve {sku} - Status code: {response.status_code}")
            return None
            
    except requests.exceptions.SSLError as ssl_error:
        # ATTEMPT 2: Fallback without SSL verification
        # This catches the specific error encountered: "no certificate or crl found"
        print(f"  ⚠ SSL error for {sku}, retrying without verification...")
        try:
            # Disable SSL warnings since we're intentionally using verify=False
            # This prevents urllib3 from spamming "InsecureRequestWarning" to console
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            response = requests.get(kitLink, headers=HEADERS, timeout=15, verify=False)
            if response.status_code == 200:
                print(f"  ✓ Fetched details for {sku} (without SSL verification)")
                return response.text
            else:
                print(f"  ✗ Failed even without SSL verification - Status code: {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"  ✗ Error on retry for {sku}: {e}")
            return None
            
    except requests.RequestException as e:
        # Catches other network errors (not SSL-related)
        print(f"  ✗ Error fetching kit details for {sku}: {e}")
        return None