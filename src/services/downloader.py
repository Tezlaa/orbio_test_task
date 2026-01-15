import io
from typing import Any

import pandas as pd


class CsvDownloadService:
    """
    Service for generating CSV files from data.
    """

    def generate_csv(self, data: list[dict[str, Any]]) -> str:
        """
        Generates a CSV string from a list of dictionaries.

        Args:
            data: List of dicts representing rows.

        Returns:
            CSV formatted string.
        """
        if not data:
            return ""

        df = pd.DataFrame(data)
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        return stream.getvalue()
