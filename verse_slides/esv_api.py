"""ESV API client for fetching scripture passages."""

import sys
import requests
from .utils import setup_logging

logger = setup_logging()

# Default API endpoint (can be overridden in config)
DEFAULT_API_ENDPOINT = "https://api.esv.org/v3/passage/text/"


class ESVAPIClient:
    """Client for interacting with Bible APIs (primarily ESV)."""

    def __init__(self, api_key, api_endpoint=None, include_headings=True):
        """Initialize the API client.

        Args:
            api_key: API authorization token
            api_endpoint: API endpoint URL (defaults to ESV API)
            include_headings: Whether to include section headings
        """
        self.api_key = api_key
        self.api_endpoint = api_endpoint or DEFAULT_API_ENDPOINT
        self.include_headings = include_headings

    def fetch_passage(self, reference):
        """Fetch a scripture passage from the ESV API.

        Args:
            reference: Scripture reference (e.g., "John 3:16-21")

        Returns:
            dict: Response containing passage text and metadata
                {
                    "text": "passage text",
                    "reference": "canonical reference",
                    "passages": ["passage text"],
                }

        Raises:
            SystemExit: If API request fails
        """
        logger.info(f"Fetching passage: {reference}")

        headers = {
            "Authorization": f"Token {self.api_key}"
        }

        params = {
            "q": reference,
            "include-passage-references": False,
            "include-verse-numbers": True,
            "include-first-verse-numbers": True,
            "include-footnotes": False,
            "include-headings": self.include_headings,
            "include-short-copyright": False,
            "indent-poetry": True,
            "indent-poetry-lines": 2,
            "line-length": 0,  # No line wrapping from API
        }

        try:
            response = requests.get(self.api_endpoint, headers=headers, params=params, timeout=10)
            logger.debug(f"API response status: {response.status_code}")

            # Handle specific error codes
            if response.status_code == 401:
                error_msg = "ESV API key is invalid. Please check your key in ~/.verse-slides/config.yaml"
                print(f"Error: {error_msg}", file=sys.stderr)
                logger.error(f"API authentication failed: 401 Unauthorized")
                sys.exit(1)

            elif response.status_code == 429:
                error_msg = "ESV API rate limit reached. Please wait a few minutes and try again."
                print(f"Error: {error_msg}", file=sys.stderr)
                logger.error("API rate limit exceeded: 429 Too Many Requests")
                sys.exit(1)

            elif response.status_code != 200:
                error_msg = f"ESV API error: {response.status_code}. See log for details."
                print(f"Error: {error_msg}", file=sys.stderr)
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                sys.exit(1)

            # Parse response
            data = response.json()
            logger.debug(f"API response data: {data}")

            # Check if we got any passages back
            if not data.get("passages") or not data["passages"][0].strip():
                error_msg = f"ESV API returned no text for '{reference}'. This may be an invalid reference."
                print(f"Error: {error_msg}", file=sys.stderr)
                logger.error(f"Empty response for reference: {reference}")
                sys.exit(1)

            # Extract canonical reference if available
            canonical_ref = reference
            if data.get("passage_meta") and data["passage_meta"]:
                canonical_ref = data["passage_meta"][0].get("canonical", reference)

            result = {
                "text": data["passages"][0],
                "reference": canonical_ref,
                "passages": data["passages"],
            }

            logger.info(f"Successfully fetched passage: {canonical_ref}")
            return result

        except requests.exceptions.ConnectionError:
            error_msg = "Cannot connect to ESV API. Check your internet connection and try again."
            print(f"Error: {error_msg}", file=sys.stderr)
            logger.error("Connection error: Unable to reach ESV API")
            sys.exit(1)

        except requests.exceptions.Timeout:
            error_msg = "ESV API request timed out. Please try again."
            print(f"Error: {error_msg}", file=sys.stderr)
            logger.error("Request timeout")
            sys.exit(1)

        except requests.exceptions.RequestException as e:
            error_msg = "Error connecting to ESV API. See log for details."
            print(f"Error: {error_msg}", file=sys.stderr)
            logger.error(f"Request exception: {e}")
            sys.exit(1)

        except Exception as e:
            error_msg = "Unexpected error fetching passage. See log for details."
            print(f"Error: {error_msg}", file=sys.stderr)
            logger.error(f"Unexpected error: {e}")
            sys.exit(1)
