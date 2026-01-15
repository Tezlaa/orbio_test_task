from typing import Any

from pydantic_ai import Agent

from src.utils.logger import logger
from src.ai.dto import AIAnalysisResult
from src.ai.prompts import SYSTEM_PROMPT, improvement_prompt
from src.config import settings


class AIService:
    """
    Service for interacting with OpenAI API using PydanticAI for structured outputs.
    """

    def __init__(self):
        self.agent = self.initial_agent()

    def initial_agent(self) -> Agent[None, AIAnalysisResult]:
        return Agent[
            None,
            AIAnalysisResult,
        ](
            settings.model_name,
            system_prompt=SYSTEM_PROMPT,
            output_type=AIAnalysisResult,
        )

    async def generate_improvements(self, reviews: list[dict[str, Any]]) -> list[str]:
        """
        Analyzes a list of reviews/summary using OpenAI to suggest improvements.
        Returns a list of formatted strings for backward compatibility.
        """
        if not self.agent:
            return ["AI Insights disabled: Missing API Key."]

        sample = self.sample_negative_reviews(reviews)

        if not sample:
            return ["No significant negative reviews found to analyze."]

        reviews_text = "\n".join([f"- {r.get('review', '')}" for r in sample])

        try:
            result = await self.agent.run(improvement_prompt(len(sample), reviews_text))
            return self.format_response(result.output)
        except Exception as e:
            logger.error(f"AI Agent error: {e}")
            return ["Failed to analyze reviews due to an AI service error."]

    def sample_negative_reviews(
        self, reviews: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        negative_reviews = [r for r in reviews if r.get("rating", 5) <= 3]
        sample_size = min(len(negative_reviews), 20)
        return negative_reviews[:sample_size]

    def format_response(self, data: AIAnalysisResult | None) -> list[str]:
        formatted_insights = []
        if not data:
            return ["No significant negative reviews found to analyze."]
        for suggestion in data.suggestions:
            formatted_insights.append(
                f"[{suggestion.priority}] {suggestion.area}: {suggestion.description}"
            )

        return formatted_insights
