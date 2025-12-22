import requests
import urllib3

'''
RETRY STRATEGY MODULE ANNOTATION:

This module provides reusable retry logic wrapper to handle SSL certificate errors gracefully.

PURPOSE:
--------
Some websites have expired/misconfigured SSL certificates. Rather than failing
completely, this retry wrapper attempts an insecure method as backup, allowing data
collection to continue while alerting us to SSL issues.

RETRY LOGIC EXPLANATION:
------------------------
The withSSLRetry wrapper uses a try-except structure with TWO attempts per request:

ATTEMPT 1 (Secure Method):
    - Executes the provided function WITH SSL certificate verification
    - This is the PROPER way to make requests (secure & encrypted)
    - Will succeed if the website has valid SSL certificates
    
ATTEMPT 2 (Fallback Method):
    - Only runs if ATTEMPT 1 throws an SSLError
    - Executes the provided function WITHOUT SSL certificate verification (verify=False)
    - This bypasses certificate validation completely
    - Less secure, but allows data collection to continue
    
WHY THIS APPROACH?
    - Some websites have expired/misconfigured SSL certificates
    - Rather than failing completely, we attempt the insecure method as backup
    - The ⚠ warning symbol alerts us when the fallback is used
    - We can investigate SSL issues later without blocking our scraping work

WHEN ATTEMPT 2 RUNS:
    - SSL certificate can't be verified (expired, self-signed, wrong domain, etc.)
    - Connection still encrypted, but we can't verify server identity
    
WHY DISABLE WARNINGS?
    - When verify=False is used, urllib3 spams warnings to console
    - We already print our own warning message (⚠ symbol)
    - Disabling prevents duplicate/redundant warning spam
    - Makes output cleaner and easier to read
'''


def withSSLRetry(requestFunc, contextName="request"):
    """
    WITH SSL RETRY ANNOTATION:
    
    Wrapper function that executes a request function with two-tier SSL retry logic.
    
    Args:
        requestFunc: A callable that takes a 'verify' parameter and returns (result, status_code)
        contextName: Name for logging purposes (default: "request")
        
    Returns:
        Tuple of (result, success_flag)
        - (result, True) if successful
        - (None, False) if failed
        
    RETRY LOGIC:
        TIER 1: Execute requestFunc with verify=True (secure & proper)
        TIER 2: If SSL fails, retry with verify=False (fallback)
        
    USAGE:
        def my_request(verify=True):
            response = requests.get(url, verify=verify)
            return response.text, response.status_code
            
        result, success = withSSLRetry(my_request, "my page")
    """
    try:
        # ATTEMPT 1: Secure method with SSL verification
        result, status_code = requestFunc(verify=True)
        if status_code == 200:
            return result, True
        else:
            print(f"  ✗ Failed to retrieve {contextName} - Status code: {status_code}")
            return None, False
            
    except requests.exceptions.SSLError as ssl_error:
        # ATTEMPT 2: Fallback without SSL verification
        # Triggered when: SSL certificate is invalid, expired, or can't be verified
        print(f"  ⚠ SSL error on {contextName}, retrying without verification...")
        try:
            # Disable SSL warnings since we're intentionally using verify=False
            # This prevents urllib3 from spamming "InsecureRequestWarning" to console
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            result, status_code = requestFunc(verify=False)
            if status_code == 200:
                return result, True
            else:
                print(f"  ✗ Failed even without SSL verification - Status code: {status_code}")
                return None, False
        except requests.RequestException as e:
            print(f"  ✗ Error on retry for {contextName}: {e}")
            return None, False
            
    except requests.RequestException as e:
        # Catches other network errors (timeout, connection refused, DNS failure, etc.)
        print(f"  ✗ Error fetching {contextName}: {e}")
        return None, False