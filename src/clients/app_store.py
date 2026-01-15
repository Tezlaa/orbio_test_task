from typing import Any

from src.clients.base import BaseAsyncClient


class AppStoreClient(BaseAsyncClient):
    """
    Client for interacting with the Apple App Store / iTunes Search API.
    """

    BASE_URL = "https://itunes.apple.com/"

    async def get_reviews(
        self, app_id: str, country: str = "us", page: int = 1
    ) -> tuple[dict[str, Any] | None, bool]:
        """
        Fetches reviews via RSS feed.

        Args:
            app_id: The ID of the application.
            country: Two-letter country code.
            page: Page number to fetch.

        Returns:
            (response_dict, is_error)
        """
        return await self._request(
            method="GET",
            endpoint=f"{country}/rss/customerreviews/page={page}/id={app_id}/sortBy=mostRecent/json",
        )

    async def get_app_id(
        self,
        app_name: str,
        country: str = "us",
        limit: int = 1,
        entity: str = "software",
    ) -> tuple[dict[str, Any] | None, bool]:
        """
        Searches for an App ID by name.

        Args:
            app_name: Name of the app to search for.
            country: Two-letter country code.
            limit: Max number of results.
            entity: Type of entity to search for.

        Returns:
            (response_dict, is_error)
        """
        return await self._request(
            method="GET",
            endpoint=f"search?term={app_name}&country={country}&entity={entity}&limit={limit}",
        )
