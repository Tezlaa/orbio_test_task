from typing import Optional

from pydantic import BaseModel


class ReviewRequest(BaseModel):
    """
    Request model for analyzing app store reviews.
    """

    app_name: str
    app_id: Optional[str] = None
    country: str = "us"
    count: int = 100


class MetricsResponse(BaseModel):
    """
    Response model containing calculated metrics from reviews.
    """

    average_rating: float
    rating_distribution: dict[str, float]
    total_reviews: int


class InsightsResponse(BaseModel):
    """
    Response model containing sentiment insights and common keywords.
    """

    sentiment_distribution: dict[str, int]
    negative_common_keywords: list[tuple[str, int]]
    actionable_insights: list[str]


class FullReportResponse(BaseModel):
    """
    Complete report response combining metrics, insights, and a sample of reviews.
    """

    app_name: str
    metrics: MetricsResponse
    insights: InsightsResponse
    reviews_sample: list[dict]  # For basic display, not full download
