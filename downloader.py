"""
Main script for downloading build instruction PDFs for model kits.

This program emphasizes modular code design by separating concerns into distinct modules:
- normalizer: Handles name standardization and cleanup
- managePDF: Manages PDF link extraction and file download operations
- scraper: Handles web scraping and search result parsing
- utils: Handles JSON loading and file path operations
- downloadOrchestrator: Coordinates the download process for multiple kits
- config: Centralizes configuration values like paths and constants
"""

from lib_downloader.utils import loadKitsFromJson, ensurePdfFolderExists
from lib_downloader.downloadOrchestrator import processAllKits

if __name__ == "__main__":
    # Ensure output directory exists
    ensurePdfFolderExists()
    
    # Load kits from configuration file
    kits = loadKitsFromJson()
    
    print(f"Loaded {len(kits)} kits from configuration")
    
    # Process all kits
    successful, failed = processAllKits(kits)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Download Summary:")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Total: {len(kits)}")
    print(f"{'='*60}")
