"""
Utility for loading stop words from various sources.
"""

import os
from typing import Optional

from nltk.corpus import stopwords

from src.utils.logger import logger


class StopWordsLoader:
    """
    Handles loading of stop words for text analysis.
    Prioritizes custom file-based stop words over NLTK's default lists.
    """

    STOPWORDS_DIR = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "resources", "stopwords"
    )

    @classmethod
    def get_stopwords(cls, language: str | set[str]) -> set[str]:
        """
        Retrieves stop words for a given language or set of languages.

        Args:
            language: A language code (e.g., 'english') or a set of language codes.

        Returns:
            A set of unique stop words.
        """
        # Handle multiple languages (e.g. for countries with multiple official languages)
        if isinstance(language, set):
            result = set()
            for lang in language:
                result.update(cls._search_stopwords(lang))
            return result

        return cls._search_stopwords(language)

    @classmethod
    def _search_stopwords(cls, language: str) -> set[str]:
        """
        Searches for stop words for a specific language.
        Priority:
        1. Custom file in resources/stopwords/{language}.txt
        2. NLTK stopwords
        3. Fallback to English NLTK stopwords

        Args:
            language: The language to search for.

        Returns:
            A set of stop words.
        """
        # 1. Try to load from custom file
        custom_stopwords = cls._load_from_file(language)
        if custom_stopwords:
            return custom_stopwords

        # 2. Try to load from NLTK
        try:
            return set(stopwords.words(language))
        except (OSError, LookupError):
            logger.warning(
                f"Stopwords not found for language '{language}' in NLTK. Falling back to English."
            )
            # 3. Fallback to English
            return set(stopwords.words("english"))

    @classmethod
    def _load_from_file(cls, language: str) -> Optional[set[str]]:
        """
        Loads stop words from a custom text file.

        Args:
            language: The language name (used as filename).

        Returns:
            A set of stop words if file exists, else None.
        """
        file_path = os.path.join(cls.STOPWORDS_DIR, f"{language}.txt")
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return {line.strip().lower() for line in f if line.strip()}
        except Exception as e:
            logger.error(f"Error reading custom stopwords file for {language}: {e}")
            return None
