from lib.fetchWeb import fetchListings, fetchKitDetails
from lib.scraper import parseListings, parseKitDetails
from lib.manageJSON import append_to_json

'''
MODULAR CODE ANNOTATION:
- This main.py file orchestrates the overall flow of the program
by utilizing functions from the fetchWeb and scraper modules.

- fetchWeb module is responsible for fetching HTML content from the web.

- scraper module is responsible for parsing the fetched HTML to extract relevant data.

- By modularizing the logic into separate modules (files), we keep main.py 
clean and easy to understand thus maintain.

- This way, if any issues arise or devs want to extend functionality, 
they can easily pinpoint which module to debug or add onto and have a 
focused codebase to work with
'''

if __name__ == "__main__":
    print("Starting to scrape kit listings...\n")
    
    # Fetch kit listings pages (generator yields multiple pages)
    for html in list(fetchListings()):
        # Skip if page fetch failed
        if html is None:
            print("⚠️  Skipping to next page due to fetch failure...\n")
            continue
            
        # Parse the current page to get kit links
        kitsToScrape = parseListings(html)
        
        print(f"Found {len(kitsToScrape)} kits on this page\n")
        
        # For each kit link on this page, fetch detailed info and parse it and add it to the JSON file
        for sku in kitsToScrape:
            print(f"Scraping kit: {sku}")
            
            # Fetch the detailed HTML for this specific kit
            kit_html = fetchKitDetails(sku)
            
            if kit_html is None:
                print(f"⚠️  Failed to fetch details, skipping...\n")
                continue
            
            # Parse the kit details
            details = parseKitDetails(kit_html, sku)
            print(f"  ✓ Details: {details}\n")
            
            append_to_json(details)
        
        print("-" * 60)  # Separator between pages
    
    print("\nScraping complete!")
