"""
Main script for downloading build instruction PDFs for model kits.

This program emphasizes modular code design by separating concerns into distinct modules:
- normalizer: Handles name standardization and cleanup
- managePDF: Manages PDF link extraction and file download operations
- scraper: Handles web scraping and search result parsing
- config: Centralizes configuration values like paths and constants

This separation makes the code more maintainable, testable, and reusable across different parts
of the project.
"""

import json
from lib_downloader.normalizer import normalizeName
from lib_downloader.managePDF import getPdfLink, downloadPdf
from lib_downloader.scraper import searchBuildInstructions
from lib_downloader.config import PDF_FOLDER, JSON_PATH
import os

if __name__ == "__main__":
    # Load the list of kits from JSON file
    # This file contains name and SKU information for each model kit
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        kits = json.load(f)
    
    # Process each kit in the list
    for kit in kits:
        name = kit.get("name")
        sku = kit.get("sku")
        
        # Skip kits that are missing required fields
        # Both name and SKU are necessary for searching and naming the file
        if not name or not sku:
            continue
        
        print(f"\nSearching instructions for: {name}")
        
        # Search for potential instruction pages using the scraper module
        # This returns a list of candidate pages that might contain PDFs
        candidates = searchBuildInstructions(name)
        downloaded = False
        
        # If no search results found, log it and move to next kit
        if not candidates:
            print(f"No candidates found for {name} ({sku})")
            continue
        
        # Try each candidate page until we successfully download a PDF
        # Candidates are tried in order of search relevance
        for idx, cand in enumerate(candidates, start=1):
            print(f"  Trying candidate {idx}: {cand['title']} -> {cand['url']}")
            
            # Extract the PDF link from the candidate page
            # The page itself might not be a PDF, but contain a link to one
            pdfUrl = getPdfLink(cand["url"])
            
            if pdfUrl:
                # Create a safe filename using SKU and normalized name
                # Replace spaces with underscores to avoid filesystem issues
                safeName = f"{sku}_{normalizeName(name).replace(' ', '_')}.pdf"
                filepath = os.path.join(PDF_FOLDER, safeName)
                
                # Attempt to download the PDF
                # If successful, mark as downloaded and stop trying other candidates
                if downloadPdf(pdfUrl, filepath):
                    downloaded = True
                    break  # Stop at first successful download to avoid duplicates
        
        # If we exhausted all candidates without success, log the failure
        # This helps identify kits that may need manual intervention
        if not downloaded:
            print(f"No valid PDF found for {name} ({sku}) after trying all candidates.")
