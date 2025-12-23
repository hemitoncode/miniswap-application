import os 
# -------------------------
# Config
# -------------------------
JSON_PATH = "output.json"
DELAY_BETWEEN_REQUESTS = 1
MAX_RETRIES = 3
SEARCH_URL = "https://buildinstructions.com/?s="
PDF_FOLDER = "pdfs"

os.makedirs(PDF_FOLDER, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}
