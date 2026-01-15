SYSTEM_PROMPT = """
You are an expert Product Manager analyzing App Store reviews. Extract actionable improvements.
"""


def improvement_prompt(sample_size: int, reviews_text: str) -> str:
    return (
        f"Here are {sample_size} negative reviews for an mobile app. "
        "Identify the top 3-5 most critical areas for improvement. "
        "Focus on technical issues, UX problems, or missing features."
        f"Reviews:\n{reviews_text}"
    )
