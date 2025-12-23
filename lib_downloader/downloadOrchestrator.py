
from .normalizer import normalizeName
from .managePDF import getPdfLink, downloadPdf
from .scraper import searchBuildInstructions
from .utils import createPdfFilepath

def tryDownloadFromCandidates(name, sku, candidates):
    """
    Attempt to download a PDF from a list of candidate pages.
    
    Tries each candidate in order until a successful download occurs.
    
    Args:
        name: The kit name
        sku: The kit SKU
        candidates: List of candidate dictionaries with 'title' and 'url' keys
    
    Returns True if download succeeded, False otherwise.
    """
    for idx, cand in enumerate(candidates, start=1):
        print(f"  Trying candidate {idx}: {cand['title']} -> {cand['url']}")
        
        # Extract the PDF link from the candidate page
        pdfUrl = getPdfLink(cand["url"])
        
        if not pdfUrl:
            continue
        
        # Create filepath and attempt download
        normalizedName = normalizeName(name)
        filepath = createPdfFilepath(sku, normalizedName)
        
        if downloadPdf(pdfUrl, filepath):
            return True  # Success - stop trying other candidates
    
    return False  # All candidates exhausted without success


def processKit(kit):
    """
    Process a single kit: search for instructions and download PDF.
    
    Args:
        kit: Dictionary containing 'name' and 'sku' fields
    
    Returns True if successfully downloaded, False otherwise.
    """
    name = kit.get("name")
    sku = kit.get("sku")
    
    # Validate required fields
    if not name or not sku:
        print(f"Skipping kit with missing name or SKU: {kit}")
        return False
    
    print(f"\nSearching instructions for: {name}")
    
    # Search for potential instruction pages
    candidates = searchBuildInstructions(name)
    
    if not candidates:
        print(f"No candidates found for {name} ({sku})")
        return False
    
    # Try downloading from each candidate
    downloaded = tryDownloadFromCandidates(name, sku, candidates)
    
    if not downloaded:
        print(f"No valid PDF found for {name} ({sku}) after trying all candidates.")
    
    return downloaded


def processAllKits(kits):
    """
    Process all kits in the list.
    
    Args:
        kits: List of kit dictionaries
    
    Returns a tuple of (successful_count, failed_count).
    """
    successful = 0
    failed = 0
    
    for kit in kits:
        if processKit(kit):
            successful += 1
        else:
            failed += 1
    
    return successful, failed
