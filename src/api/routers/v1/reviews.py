from fastapi import APIRouter, Depends, HTTPException, Response

from src.api.dependencies import (
    auth_dependency,
    get_ai_service,
    get_app_store_scraper,
    get_csv_download_service,
)
from src.models import FullReportResponse, ReviewRequest
from src.ai.ai_service import AIService
from src.services.analyzer import ReviewAnalyzer
from src.services.downloader import CsvDownloadService
from src.services.scraper import AppStoreScraper
from src.utils.logger import logger

reviews_router = APIRouter(dependencies=[Depends(auth_dependency)])


@reviews_router.post("/reviews/analyze", response_model=FullReportResponse)
async def analyze_reviews(
    request: ReviewRequest,
    scraper: AppStoreScraper = Depends(get_app_store_scraper),
    ai_service: AIService = Depends(get_ai_service),
    limit_reviews: int = 5,
) -> FullReportResponse:
    """
    Analyzes reviews for a given app.

    Args:
        request: The request body containing app details.
        scraper: Scraper service dependency.
        ai_service: AI service dependency.
        limit_reviews: Number of review samples to return in response.

    Returns:
        Full analysis report.
    """
    logger.info(f"Analyzing reviews for {request.app_name}, country={request.country}")

    reviews = await scraper.fetch_reviews(
        app_name=request.app_name,
        app_id=request.app_id,
        count=request.count,
        country=request.country,
    )

    if not reviews:
        logger.warning(f"No reviews found for {request.app_name}")
        raise HTTPException(status_code=404, detail="No reviews found or app not found")

    analyzer = ReviewAnalyzer(reviews, country=request.country)
    metrics, insights = await analyzer.analyze()

    # Augment actionable insights with AI
    ai_insights = await ai_service.generate_improvements(reviews)
    if ai_insights:
        insights.actionable_insights.extend(ai_insights)

    return FullReportResponse(
        app_name=request.app_name,
        metrics=metrics,
        insights=insights,
        reviews_sample=reviews[:limit_reviews],
    )


@reviews_router.post("/reviews/download")
async def download_reviews(
    request: ReviewRequest,
    scraper: AppStoreScraper = Depends(get_app_store_scraper),
    csv_service: CsvDownloadService = Depends(get_csv_download_service),
) -> Response:
    """
    Downloads reviews as a CSV file.

    Args:
        request: The request body containing app details.
        scraper: Scraper service dependency.
        csv_service: CSV generator service dependency.

    Returns:
        CSV file response.
    """
    logger.info(f"Downloading reviews for {request.app_name}")

    reviews = await scraper.fetch_reviews(
        app_name=request.app_name,
        app_id=request.app_id,
        count=request.count,
        country=request.country,
    )

    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found")

    return Response(
        content=csv_service.generate_csv(reviews),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={request.app_name}_reviews.csv"
        },
    )
