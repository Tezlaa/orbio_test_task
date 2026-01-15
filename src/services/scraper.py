import random
from typing import Any, Optional

from src.clients.app_store import AppStoreClient
from src.utils.logger import logger


class AppStoreScraper:
    """
    Service for scraping and fetching reviews from the Apple App Store.
    Does not use official API for reviews as it requires authentication/ownership,
    uses RSS feeds instead.
    """

    def __init__(self, app_store_client: AppStoreClient):
        self.app_store_client = app_store_client

    async def fetch_reviews(
        self,
        app_name: str,
        country: str = "us",
        app_id: Optional[str] = None,
        count: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Fetches reviews for a specified app using iTunes RSS feed.

        Args:
            app_name: Name of the app (used for ID lookup if ID not provided).
            country: Country code for the store region.
            app_id: Specific App ID if known.
            count: Number of reviews to attempt to fetch.

        Returns:
            A list of review dictionaries.
        """
        # 1. Resolve App ID if not provided
        if not app_id:
            app_id = await self._search_app_id(app_name, country=country)

        if not app_id:
            logger.error(f"Could not find App ID for {app_name}")
            return []

        all_reviews = []
        page = 1

        # We need to fetch enough pages to meet the count requirement.
        # RSS usually returns 50 items per page.
        # We fetch extra to allow for some filtering or randomization if needed.
        target_pool = count * 2

        while len(all_reviews) < target_pool and page <= 10:
            try:
                data, is_error = await self.app_store_client.get_reviews(
                    app_id=app_id,
                    country=country,
                    page=page,
                )
                if is_error:
                    break

                entries = data.get("feed", {}).get("entry", [])

                if not entries:
                    break

                for entry in entries:
                    review = {
                        "id": entry.get("id", {}).get("label"),
                        "title": entry.get("title", {}).get("label"),
                        "review": entry.get("content", {}).get("label"),
                        "rating": int(entry.get("im:rating", {}).get("label", 0)),
                        "date": entry.get("updated", {}).get("label"),
                        "userName": entry.get("author", {})
                        .get("name", {})
                        .get("label"),
                    }
                    all_reviews.append(review)

                page += 1

            except Exception as e:
                logger.error(f"Error fetching reviews page {page}: {e}")
                break

        if not all_reviews:
            return []

        # If we fetched more than requested, return a random sample to be representative
        if len(all_reviews) > count:
            return random.sample(all_reviews, count)

        return all_reviews

    async def _search_app_id(self, app_name: str, country: str = "us") -> Optional[str]:
        """
        Attempts to find the App ID using the iTunes Search API.

        Args:
            app_name: Name of the app.
            country: Store country.

        Returns:
            App ID as string or None if not found.
        """
        try:
            data, is_error = await self.app_store_client.get_app_id(
                app_name, country=country
            )
            if not is_error and data and data.get("resultCount", 0) > 0:
                return str(data["results"][0]["trackId"])

        except Exception as e:
            logger.error(f"Error searching app ID for '{app_name}': {e}")
            pass
        return None
