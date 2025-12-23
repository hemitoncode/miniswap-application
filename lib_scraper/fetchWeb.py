import requests
import certifi
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
- /show-40 shows 40 kits per page to reduce the number of pages we have to iterate through (this way we have less requests overall)
- /page- is the pagination segment to get different pages of listings. I will be iterating through 
  multiple pages starting from page 25 to get all 2024 kits.
'''

BASE_KIT_LISTING = 'https://miniset.net/sets/games-workshop/sort-new/type-miniature/kind-not3d/view-details/show-40/page-'

# These are the ranges of page which contain 2024 kits
# This way we do not have to scrape all pages for this catalog
START_PAGE = 13
END_PAGE = 26

# HTTP headers to make requests appear browser-like (helps avoid blocks and SSL issues)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

'''
SESSION OBJECT ANNOTATION:

Using a persistent requests.Session object for connection pooling and reuse.

BENEFITS OF SESSION OBJECT:
----------------------------
1. CONNECTION POOLING: Reuses TCP connections across multiple requests
   - SSL handshake happens once per connection instead of every request
   - Significantly faster for multiple requests to the same host
   - Reduces intermittent SSL errors by minimizing handshake frequency

2. PERSISTENT HEADERS: Headers are set once on the session, not per request
   - Cleaner code, less repetition
   - Consistent headers across all requests

3. CERTIFICATE MANAGEMENT: Using certifi.where() for up-to-date CA bundle
   - certifi provides Mozilla's carefully curated CA certificate bundle
   - Automatically includes intermediate certificates
   - More reliable than system certificates which may be outdated

4. HTTP CONNECTION REUSE: Keep-alive connections maintained automatically
   - Multiple requests over same TCP connection
   - Lower latency for subsequent requests
   - More efficient network usage

5. CONNECTION POOL SETTINGS: Configured to handle stale connections
   - max_retries=3: Automatically retry failed connections
   - pool_connections: Number of connection pools to cache
   - pool_maxsize: Maximum connections to save in the pool

WHY THIS HELPS WITH SSL AND TIMEOUT ISSUES:
--------------------------------------------
- Fewer SSL handshakes = fewer opportunities for SSL failures
- Up-to-date CA bundle = better certificate validation
- Connection reuse = more stable connection to the same server
- Automatic retries handle transient network issues
- Reduces impact of load balancer server inconsistencies
'''

# Configure retry strategy for the session
retry_strategy = Retry(
    total=3,                    # Total number of retries
    backoff_factor=1,           # Wait 1, 2, 4 seconds between retries
    status_forcelist=[429, 500, 502, 503, 504],  # Retry on these HTTP status codes
    allowed_methods=["GET"]     # Only retry GET requests
)

# Create HTTP adapter with retry strategy
adapter = HTTPAdapter(
    max_retries=retry_strategy,
    pool_connections=10,        # Number of connection pools to cache
    pool_maxsize=20            # Max connections to save in pool
)

# Create persistent session object for all requests
session = requests.Session()
session.mount("https://", adapter)  # Apply adapter to HTTPS requests
session.mount("http://", adapter)   # Apply adapter to HTTP requests
session.headers.update(HEADERS)
session.verify = certifi.where()    # Use certifi's up-to-date CA certificate bundle


'''
HELPER FUNCTIONS ANNOTATION:

- Helper functions to fetch web pages
- fetchListings: Fetches HTML content of kit listings pages, iterating through multiple pages
  starting from START_PAGE and continuing through END_PAGE.
- fetchKitDetails: Fetches detailed HTML content for a specific kit based on sku link which is 
  retrieved from parsing HTML of the kit listing page.
  
Both functions use the persistent SESSION OBJECT for connection pooling:
  - Reuses TCP connections across multiple requests
  - Performs SSL handshake once per connection instead of per request
  - Uses certifi's up-to-date CA certificate bundle for better SSL validation
  - Maintains keep-alive connections automatically
  
This approach reduces intermittent SSL errors by minimizing the number of SSL handshakes
and ensures we're using the most current certificate validation.
'''


def fetchListings():
    """
    FETCH LISTING ANNOTATION:

    Generator function that fetches kit listing pages sequentially.
    Starts at START_PAGE and fetches through END_PAGE.
    Yields HTML content for each successfully fetched page.
    
    CONNECTION STRATEGY:
    --------------------
    Uses the persistent session object which:
    - Reuses the same TCP connection across multiple page requests
    - Performs SSL handshake only when establishing new connections
    - Automatically handles keep-alive and connection pooling
    - Uses certifi's CA bundle for reliable certificate validation
    - Automatically retries failed requests (3 attempts with backoff)
    
    TIMEOUT HANDLING:
    -----------------
    - Connect timeout: 10 seconds (time to establish connection)
    - Read timeout: 30 seconds (time to receive response after connection)
    - Longer read timeout handles slow server responses
    - Separate timeouts allow distinguishing connection vs server issues
    
    This significantly reduces the chance of intermittent SSL errors since
    we're not renegotiating SSL for every single page request.
    """
    for currentPage in range(START_PAGE, END_PAGE + 1):
        print(f"Fetching listings page: {currentPage}")
        kitListingsLink = f"{BASE_KIT_LISTING}{currentPage}"
        
        # Add delay between requests to be polite and avoid rate limiting
        time.sleep(0.5)
        
        try:
            # Use session object with separate connect and read timeouts
            # Format: timeout=(connect_timeout, read_timeout)
            response = session.get(kitListingsLink, timeout=(10, 30))
            if response.status_code == 200:
                yield response.text
            else:
                print(f"  ✗ Failed to retrieve page {currentPage} - Status code: {response.status_code}")
                yield None
        except requests.exceptions.Timeout:
            print(f"  ✗ Timeout error on page {currentPage} - server took too long to respond")
            yield None
        except requests.RequestException as e:
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
        
    CONNECTION STRATEGY:
    --------------------
    Uses the persistent session object which:
    - Reuses TCP connections from the connection pool
    - Minimizes SSL handshakes by maintaining persistent connections
    - Provides more stable connections to miniset.net servers
    - Uses certifi's CA bundle for up-to-date certificate validation
    - Automatically retries failed requests (3 attempts with backoff)
    
    TIMEOUT HANDLING:
    -----------------
    - Connect timeout: 10 seconds (time to establish connection)
    - Read timeout: 30 seconds (time to receive response after connection)
    - Longer read timeout handles slow server responses
    - Separate timeouts allow distinguishing connection vs server issues
    
    Since we're making many sequential requests for kit details, connection
    reuse provides significant performance benefits and stability improvements.
    """
    kitLink = f"https://miniset.net/sets/gw-{sku}"
    
    # Add small delay between requests to be polite and avoid rate limiting
    time.sleep(0.3)
    
    try:
        # Use session object with separate connect and read timeouts
        # Format: timeout=(connect_timeout, read_timeout)
        response = session.get(kitLink, timeout=(10, 30))
        if response.status_code == 200:
            print(f"  ✓ Fetched details for {sku}")
            return response.text
        else:
            print(f"  ✗ Failed to retrieve {sku} - Status code: {response.status_code}")
            return None
    except requests.exceptions.Timeout:
        print(f"  ✗ Timeout error for {sku} - server took too long to respond")
        return None
    except requests.RequestException as e:
        print(f"  ✗ Error fetching kit details for {sku}: {e}")
        return None