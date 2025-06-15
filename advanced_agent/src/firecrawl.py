"""
This module provides a service for interacting with the Firecrawl API to search and scrape company information.
"""

import logging
import os
from typing import List

from dotenv import load_dotenv
from firecrawl import FirecrawlApp, ScrapeOptions

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class FirecrawlService:
    """
    Service for interacting with Firecrawl API to search and scrape company information.
    This service uses the FirecrawlApp to perform searches and scrape web pages for company data.
    It requires the FIRECRAWL_API_KEY environment variable to be set.
    """

    def __init__(self):
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY environment variable is not set.")
        self.app = FirecrawlApp(api_key=api_key)

    def search_companies(self, query: str, num_results: int = 5) -> List:
        """
        Search for companies related to the given query using Firecrawl.
        Args:
            query (str): The search query to find companies.
            num_results (int): The number of results to return. Default is 5.
        Returns:
            List: A list of search results containing company information.
        """
        try:
            results = self.app.search(
                query=f"{query} company pricing",
                limit=num_results,
                scrape_options=ScrapeOptions(
                    formats=["markdown"],
                ),
            )
            return results
        except Exception as e:
            logging.error(f"Error during search: {e}")
            return []

    def scrape_company_pages(self, url: str) -> str:
        """
        Scrape the content of a company page using Firecrawl.
        Args:
            url (str): The URL of the company page to scrape.
        Returns:
            str: The scraped content of the page.
        """
        try:
            result = self.app.scrape_url(
                url,
                formats=["markdown"],
            )
            return result
        except Exception as e:
            logging.error(f"Error during scraping: {e}")
            return ""
