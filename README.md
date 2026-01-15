# Apple Store Review Analysis API
## DEMO URL: http://13.60.31.58:1992/

This project provides a robust API for collecting, processing, and analyzing reviews from the Apple App Store. It is designed to extract actionable insights, such as sentiment distribution and common negative keywords, to help app developers improve their products.


## 🚀 Features

-   **Review Collection:** automated fetching of reviews for a specified App ID.
-   **Sentiment Analysis:** detailed breakdown of user sentiment (Positive, Neutral, Negative).
-   **Keyword Extraction:** identifies common terms associated with negative feedback.
-   **AI Analysis:** uses LLMs to synthesize negative feedback into human-readable suggestions.
-   **Actionable Insights:** generates summaries to highlight areas for improvement.
-   **Demo Dashboard:** a simple web interface to visualize the data.

## 🛠️ Tech Stack

-   **Language:** Python 3.12+
-   **Framework:** FastAPI (High-performance API)
-   **AI/LLM:** OpenAI GPT-4o-mini (via PydanticAI)
-   **NLP:** NLTK (Natural Language Toolkit) for tokenization and stop-word removal.
-   **Containerization:** Docker & Docker Compose
-   **Frontend (Demo):** Vanilla JavaScript, HTML5, CSS3

## 🏃‍♂️ Running Locally

### Prerequisites

-   Python 3.12 or higher
-   Docker & Docker Compose (optional, for containerized run)

### Option 1: Using Docker (Recommended)

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd orbio_test_task
    ```

2.  **Set up Environment Variables:**
    Copy `example.env` to `.env`:

    ```bash
    cp example.env .env
    ```

    Set up environment variables:
    ```bash
    OPENAI_API_KEY=...
    PASSWORD="..."
    ```
    `PASSWORD` is used for the demo dashboard. (for avoid unauthorized access. Someone will spend my tokens :D )

    Also Set up demo backend url in `demo/backendUrl.js` for localy test.:
    ```js
    const BackendURL = "http://localhost:9999/api/v1";
    ```

3.  **Start the services:**

    ```bash
    docker-compose up --build
    ```

4.  **Access the Application:**
    -   **API Documentation (Swagger UI):** [http://localhost:9999/docs](http://localhost:9999/docs)
    -   **Demo Dashboard:** [http://localhost:1992](http://localhost:1992)

### Option 2: Manual Setup (Python)

1.  **Create a Virtual Environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the API:**

    ```bash
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
    ```

4.  **Access the API:**
    -   Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.

## 🧠 Approach & Design Decisions

### Architecture

The project follows a modular **Service-Layer Architecture** to ensure separation of concerns and maintainability:

-   **`src/api`**: Handles HTTP requests and response validation (FastAPI Routers).
-   **`src/services`**: Contains the core business logic (e.g., `ReviewService` for orchestration, `AnalysisService` for processing).
-   **`src/clients`**: specialized modules for external communication (e.g., fetching data from Apple's RSS feed).
-   **`src/ai`**: dedicated module for NLP tasks, keeping AI logic decoupled from general application code.

### Text Processing & Insight Generation

1.  **Data Fetching**: Reviews are fetched from the public RSS feed of the Apple App Store.
2.  **Normalization**: Text is cleaned (lowercased, special characters removed) and tokenized using `nltk.word_tokenize`.
3.  **Sentiment Scoring**: We calculate a sentiment score based on rating and keyword polarity.
4.  **Keyword Analysis**: Stop words are removed to filter noise. We then tabulate frequencies of terms appearing specifically in negative reviews (1-2 stars) to surface "pain points" (e.g., "login", "crash", "subscription").
5.  **LLM Integration**: A subset of negative reviews is sent to an **OpenAI GPT-4o-mini** model (orchestrated via **PydanticAI**). The model is prompted to act as a Product Manager, analyzing the specific text of the reviews to provide 3 prioritized, structured suggestions for improvement. This goes beyond simple keyword counting by understanding context (e.g., distinguishing between "login failed" and "login confusing").

## 📊 Sample Report

Here is an example of the analysis output for the **Instagram** app:

```json
{
    "app_name": "instagram",
    "metrics": {
        "average_rating": 2.09,
        "total_reviews": 100,
        "rating_distribution": {
            "1": 65.0,
            "2": 6.0,
            "3": 5.0,
            "4": 3.0,
            "5": 21.0
        }
    },
    "insights": {
        "sentiment_distribution": {
            "Neutral": 47,
            "Positive": 28,
            "Negative": 25
        },
        "negative_common_keywords": [
            ["account", 16],
            ["suspended", 5],
            ["crash", 4]
        ],
        "actionable_insights": [
            "Common themes in negative reviews: account, suspended, crash"
        ]
    }
}
```
