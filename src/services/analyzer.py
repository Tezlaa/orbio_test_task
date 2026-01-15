import asyncio
import re
from collections import Counter
from typing import Any

import nltk
import pandas as pd
from nltk.tokenize import word_tokenize
from textblob import TextBlob

from src.models import InsightsResponse, MetricsResponse
from src.utils.stopwords_loader import StopWordsLoader

# Ensure NLTK data is available
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab")
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")


class ReviewAnalyzer:
    """
    Analyzes app reviews to extract metrics, sentiment, and insights.
    Uses pandas for data manipulation and TextBlob/NLTK for NLP.
    """

    COUNTRY_TO_LANGUAGE = {
        "us": "english",
        "gb": "english",
        "au": "english",
        "ca": "english",
        "de": "german",
        "es": "spanish",
        "fr": "french",
        "it": "italian",
        "ua": {
            "ukrainian",
            "russian",
            "english",
        },
        "pt": "portuguese",
        "pl": "polish",
        "br": "portuguese",
        "nl": "dutch",
    }

    def __init__(self, reviews: list[dict[str, Any]], country: str = "us"):
        """
        Initialize the analyzer with a list of reviews.

        Args:
            reviews: List of review dicts.
            country: Country code to determine language for stop words.
        """
        self.df = pd.DataFrame(reviews)
        self.language: str | set[str] = self.COUNTRY_TO_LANGUAGE.get(
            country.lower(), "english"
        )
        self.stop_words = None

    async def analyze(self) -> tuple[MetricsResponse, InsightsResponse]:
        """
        Runs the full analysis pipeline asynchronously using a thread pool.
        This prevents blocking the main event loop during heavy text processing.

        Returns:
            (MetricsResponse, InsightsResponse)
        """
        return await asyncio.to_thread(self._analyze_sync)

    def _analyze_sync(self) -> tuple[MetricsResponse, InsightsResponse]:
        """
        Internal synchronous wrapper for the analysis pipeline.
        """
        self._process_data()
        metrics = self._calculate_metrics()
        insights = self._generate_insights()
        return metrics, insights

    def _process_data(self) -> None:
        """
        Preprocesses the review data (cleaning text, ensuring columns).
        """
        if self.df.empty:
            return

        required = ["review", "rating", "title"]
        for col in required:
            if col not in self.df.columns:
                self.df[col] = None

        self.df["clean_review"] = self.df["review"].apply(self._clean_text)

    def _clean_text(self, text: str) -> str:
        """
        Cleans text by lowering case and removing special characters.
        """
        if not isinstance(text, str):
            return ""
        text = text.lower()
        # Remove special chars but keep whitespace and alphanumerics
        text = re.sub(r"[^\w\s]", "", text)
        return text

    def _calculate_metrics(self) -> MetricsResponse:
        """
        Calculates basic stats like average rating and distribution.
        """
        if self.df.empty:
            return MetricsResponse(
                average_rating=0.0, rating_distribution={}, total_reviews=0
            )

        avg_rating = float(self.df["rating"].mean())

        rating_counts = self.df["rating"].value_counts().to_dict()
        total_reviews = len(self.df)
        distribution = {
            str(k): (v / total_reviews) * 100 for k, v in rating_counts.items()
        }

        return MetricsResponse(
            average_rating=round(avg_rating, 2),
            rating_distribution=distribution,
            total_reviews=total_reviews,
        )

    def _generate_insights(self) -> InsightsResponse:
        """
        Generates sentiment insights and key themes.
        """
        if self.df.empty:
            return InsightsResponse(
                sentiment_distribution={},
                negative_common_keywords=[],
                actionable_insights=[],
            )

        self.df["sentiment_score"] = self.df["review"].apply(
            lambda x: TextBlob(str(x)).sentiment.polarity
        )
        self.df["sentiment_category"] = self.df["sentiment_score"].apply(
            self._categorize_sentiment
        )

        sentiment_dist = self.df["sentiment_category"].value_counts().to_dict()

        negative_reviews = self.df[self.df["sentiment_category"] == "Negative"]
        neg_keywords = self._extract_common_keywords(negative_reviews["clean_review"])

        insights = []
        if sentiment_dist.get("Negative", 0) > len(self.df) * 0.3:
            insights.append(
                "High volume of negative sentiment. Investigate common complaints."
            )

        if neg_keywords:
            common_issues = ", ".join([k[0] for k in neg_keywords[:3]])
            insights.append(f"Common themes in negative reviews: {common_issues}")

        return InsightsResponse(
            sentiment_distribution=sentiment_dist,
            negative_common_keywords=neg_keywords,
            actionable_insights=insights,
        )

    def _categorize_sentiment(self, score: float) -> str:
        if score > 0.1:
            return "Positive"
        elif score < -0.1:
            return "Negative"
        else:
            return "Neutral"

    def _extract_common_keywords(
        self,
        text_series: pd.Series,
        top_n: int = 10,
    ) -> list[tuple[str, int]]:
        """
        Extracts most common words from a pandas Series of text, excluding stop words.
        """
        all_text = " ".join(text_series.astype(str).tolist())
        tokens = word_tokenize(all_text)
        stop_words = self.__get_stop_words()

        filtered_tokens = [
            w for w in tokens if w not in stop_words and len(w) > 2 and not w.isdigit()
        ]

        counter = Counter(filtered_tokens)
        return counter.most_common(top_n)

    def __get_stop_words(self) -> set[str]:
        return StopWordsLoader.get_stopwords(self.language)

    def get_raw_data(self) -> list[dict[str, Any]]:
        return self.df.to_dict(orient="records")
