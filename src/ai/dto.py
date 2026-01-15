from typing import Literal
from pydantic import BaseModel, Field


class ImprovementSuggestion(BaseModel):
    """
    Structured suggestion for improvement based on user feedback.
    """

    area: str = Field(description="The specific area of the app needing improvement")
    description: str = Field(
        description="A concise description of the issue and how to fix it"
    )
    priority: Literal["High", "Medium", "Low"] = Field(
        description="Priority level: High, Medium, or Low"
    )


class AIAnalysisResult(BaseModel):
    suggestions: list[ImprovementSuggestion]
