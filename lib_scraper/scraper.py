from bs4 import BeautifulSoup
from .sanitizer import sanitizeYear, sanitizeSKU

def parseListings(html):
    # All 2024 kit detail links to scrape will be stored here
    kitsToScrape = []

    soup = BeautifulSoup(html, 'html.parser')

    # Find table containing kit listings
    table = soup.find('table', {'class': 'views-table'})
    
    if not table:
        print("⚠️  WARNING: No table with class 'views-table' found on this page")
        return kitsToScrape

    # There is no header row in the table, so no need to splice index from pos 1 onwards
    for row in table.find_all('tr'):

        '''
        TD ANNOTATION: 

        <td></td> is the table data, so they contain details about each kit.
        However, this is from the general listing html page, so it doesn't have 
        all of the info. All we need is the date released and SKU to fetch detailed info later.
        '''

        details = row.find_all('td')
        
        # Skip rows that don't have at least 2 TD elements
        if len(details) < 2:
            continue
            
        td1 = details[0] # First TD contains the release date
        td2 = details[1] # Second TD contains the SKU
        
        # The release date is within a <span> with class 'date-display-single'
        releaseDate_span = td1.find('span', {'class': 'date-display-single'})
        if not releaseDate_span:
            print("SKIPPED ROW: Release date span not found")
            continue # Skip this row if release date span is not found
        releaseDate = releaseDate_span.text
        year = sanitizeYear(releaseDate) 

        if (year == '2025'):
            continue  # Skip kits from the year 2025

        # No need to check for 2023 or earlier since no pages contain those years based on manual analysis

        # We extract the link to the detailed page. Since it is the only link in this TD, we can directly find it.
        detailedPageLink = td2.find("a").get('href', '').strip()

        '''
        SKU FILTER ANNOTATION:

        - There is a id text I could've scrapped, but sanitizing the link to get the SKU 
        is more reliable since the link structure is consistent.

        - The HTML text is not part of a TD or class that we can easily target, 
        so it would be more complex to extract.

        - Instructions dictate that we must extract products with SKU starting with '99' 
        hence the conditional logic following the function call.
        '''

        sku = sanitizeSKU(detailedPageLink)
        if not sku.startswith('99'):
            continue  

        kitsToScrape.append(sku)

    return kitsToScrape


# SKU was already extracted through the listings scraping process, so we pass them as a parameters
# We could've scrapped title too, but to keep things consistent, we get all details from the detailed page
# SKU is the only exception since we needed to for the links for getting detailed page anyways

def parseKitDetails(html, sku):
    soup = BeautifulSoup(html, 'html.parser')

    # Title is within the main container div with id 'main' and h1 with class 'title'
    mainContainer = soup.find('div', {'id': 'main'})
    title = mainContainer.find('h1', {'class': 'title'}).text.strip()

    '''
    PRICE EXTRACTION ANNOTATION:
    - The last known price is located within the 'set_main_info' div container. 

    - It is found by locating the bolded text "Last known price:" and then finding the next item after it 
    using find_next_sibling method.
    '''

    lastKnownPrice = soup.find(
        "b",
        string=lambda s: s and "Last known price:" in s
    )
    lastKnownPrice = lastKnownPrice.find_next_sibling(text=True).strip()

    '''
    DESCRIPTION EXTRACTION ANNOTATION:
    - Find description in visible text container. 

    - There are multiple containers with class 'text-inner-container' (which belong to description), 
    but some are hidden via CSS styles. So we need to check their styles. 
    `display: none` means hidden, thus ignored.
    
    - To get the proper text, target the paragraph tags within the visible container. 
    '''
    
    containers = soup.find_all('div', {'class': 'text-inner-container'})
    description = None
    for container in containers:
        style = container.get('style', '')
        if 'display: none' not in style:  # match hidden style properly
            paragraphs = [p.get_text(strip=True) for p in container.find_all("p")]
            description = " ".join(paragraphs)
            break  # stop after first visible container

    detailResponse = {
        "name": title,
        "description": description,
        "last_known_price": lastKnownPrice,
        "sku": sku
    }

    return detailResponse