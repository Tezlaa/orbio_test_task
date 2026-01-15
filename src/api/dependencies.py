from fastapi import Depends, HTTPException, Header

from src.clients.app_store import AppStoreClient
from src.ai.ai_service import AIService
from src.services.downloader import CsvDownloadService
from src.services.scraper import AppStoreScraper
from src.config import settings


def auth_dependency(password: str = Header(alias="password")) -> None:
    """Dependency provider for authentication."""
    if password != settings.password:
        raise HTTPException(status_code=401, detail="Unauthorized")


def get_app_store_client() -> AppStoreClient:
    """Dependency provider for AppStoreClient."""
    return AppStoreClient()


def get_app_store_scraper(
    client: AppStoreClient = Depends(get_app_store_client),
) -> AppStoreScraper:
    """Dependency provider for AppStoreScraper, injecting AppStoreClient."""
    return AppStoreScraper(app_store_client=client)


def get_csv_download_service() -> CsvDownloadService:
    """Dependency provider for CsvDownloadService."""
    return CsvDownloadService()


def get_ai_service() -> AIService:
    """Dependency provider for OpenAIService."""
    return AIService()
