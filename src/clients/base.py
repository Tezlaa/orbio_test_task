from typing import Any, Optional

import aiohttp
from aiohttp import ClientResponse

from src.utils.logger import logger


class BaseAsyncClient:
    """
    Base asynchronous client for interacting with third-party APIs.
    Provides a wrapper around aiohttp with error handling and response parsing.
    """

    BASE_URL: str

    @staticmethod
    def _auth() -> Optional[aiohttp.BasicAuth]:
        """Provides authentication credentials if needed."""
        return None

    @staticmethod
    def _headers() -> dict[str, str]:
        """Returns default headers for requests."""
        return {}

    @staticmethod
    def _get_params() -> dict[str, Any]:
        """Returns default query parameters."""
        return {}

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> tuple[dict[str, Any] | None, bool]:
        """
        Executes an HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: URL path relative to BASE_URL
            params: Query parameters
            data: Form data
            json_data: JSON body
            headers: Custom headers

        Returns:
            A tuple of (parsed response JSON or error dict, is_error boolean).
        """
        params_ = params or self._get_params()
        headers_ = headers or self._headers()

        url = f"{self.BASE_URL}{endpoint}"
        async with (
            aiohttp.ClientSession() as session,
            session.request(
                method=method,
                url=url,
                params=params_,
                data=data,
                json=json_data,
                headers=headers_,
                auth=self._auth(),
            ) as response,
        ):
            return await self._generate_response(response)

    @staticmethod
    async def _generate_response(
        response: ClientResponse,
    ) -> tuple[dict[str, Any] | None, bool]:
        """
        Parses the client response and handles errors.

        Returns:
            (response_json, is_error)
        """
        try:
            response_text = await response.json(content_type=None)
        except Exception as e:
            logger.error(f"Error parsing JSON response: {e}")
            response_text = None

        try:
            response.raise_for_status()
        except Exception as e:
            error_message = str(e)
            logger.error(
                f"Request failed: error={error_message} status={response.status} response={response_text}"
            )
            return {"error": response_text or error_message}, True
        else:
            return response_text, False
