import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Central configuration class."""
    
    API_TOKEN = os.getenv("COC_API_TOKEN")
    CLAN_TAG = os.getenv("CLAN_TAG")
    
    # Supercell API v1 Base URL
    BASE_URL = "https://api.clashofclans.com/v1"
    
    # Validation at startup
    if not API_TOKEN:
        raise ValueError("FATAL ERROR: COC_API_TOKEN not found in .env file.")
    
    if not CLAN_TAG:
        raise ValueError("FATAL ERROR: CLAN_TAG not found in .env file.")

    # Standard headers for all requests
    HEADERS = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json"
    }