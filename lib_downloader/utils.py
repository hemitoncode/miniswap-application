import json
import os
from .config import PDF_FOLDER, JSON_PATH

def loadKitsFromJson():
    """
    Load the list of kits from the JSON configuration file.
    
    Returns a list of kit dictionaries, each containing 'name' and 'sku' fields.
    """
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def createPdfFilepath(sku, normalizedName):
    """
    Generate a safe filepath for saving a PDF.
    
    Args:
        sku: The SKU code for the kit
        normalizedName: The normalized name of the kit
    
    Returns a full filepath in the PDF_FOLDER directory.
    """
    safeName = f"{sku}_{normalizedName.replace(' ', '_')}.pdf"
    return os.path.join(PDF_FOLDER, safeName)


def ensurePdfFolderExists():
    """
    Create the PDF folder if it doesn't already exist.
    """
    os.makedirs(PDF_FOLDER, exist_ok=True)


# ============================================================================
# download_orchestrator.py
# Contains high-level logic for coordinating the download process
# ============================================================================
