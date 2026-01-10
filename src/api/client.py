import requests
from src.config import Config

class CoCClient:
    """Wrapper client to interact with Clash of Clans API."""

    def __init__(self):
        self.base_url = Config.BASE_URL
        self.headers = Config.HEADERS

    def _get(self, endpoint: str):
        """Internal helper method to handle GET requests and errors."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 403:
                print(f"[ERROR 403] Access denied. Your IP might have changed.")
            elif err.response.status_code == 404:
                print(f"[ERROR 404] Resource not found. Check if the Tag is correct.")
            else:
                print(f"[ERROR] HTTP Error: {err}")
            return None
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            return None

    def get_clan_info(self, clan_tag: str):
        """Fetches basic clan information."""
        # Encode # as %23 for the URL
        encoded_tag = clan_tag.replace("#", "%23")
        return self._get(f"/clans/{encoded_tag}")

    def get_league_group(self, clan_tag: str):
        """Fetches the current war league group (needed to access rounds)."""
        encoded_tag = clan_tag.replace("#", "%23")
        return self._get(f"/clans/{encoded_tag}/currentwar/leaguegroup")
