const API_BASE_URL = "http://localhost:9999/api/v1";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("analyzeForm");
    const loadingDiv = document.getElementById("loading");
    const resultsDiv = document.getElementById("results");
    const errorDiv = document.getElementById("error");
    const downloadBtn = document.getElementById("downloadBtn");

    let lastRequestData = null;
    let lastPassword = null;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const appName = document.getElementById("appName").value;
        const appId = document.getElementById("appId").value || null;
        const country = document.getElementById("country").value;
        const count = parseInt(document.getElementById("count").value);
        const password = document.getElementById("password").value;

        lastPassword = password;

        lastRequestData = {
            app_name: appName,
            app_id: appId,
            country: country,
            count: count,
        };

        // Reset UI
        resultsDiv.style.display = "none";
        errorDiv.textContent = "";
        loadingDiv.style.display = "block";
        downloadBtn.style.display = "none";

        try {
            const response = await fetch(`${API_BASE_URL}/reviews/analyze`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    password: password,
                },
                body: JSON.stringify(lastRequestData),
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || "Error fetching data");
            }

            const data = await response.json();
            displayResults(data);
            downloadBtn.style.display = "inline-block";
        } catch (err) {
            errorDiv.textContent = err.message;
        } finally {
            loadingDiv.style.display = "none";
        }
    });

    downloadBtn.addEventListener("click", async () => {
        if (!lastRequestData) return;

        try {
            const response = await fetch(`${API_BASE_URL}/reviews/download`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    password: lastPassword,
                },
                body: JSON.stringify(lastRequestData),
            });

            if (!response.ok) throw new Error("Download failed");

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `${lastRequestData.app_name}_reviews.csv`;
            document.body.appendChild(a);
            a.click();
            a.remove();
        } catch (err) {
            alert(err.message);
        }
    });

    function displayResults(data) {
        resultsDiv.style.display = "block";

        // Metrics
        document.getElementById("avgRating").textContent =
            data.metrics.average_rating;
        document.getElementById("totalReviews").textContent =
            data.metrics.total_reviews;

        // Insights
        document.getElementById("sentimentDist").textContent = JSON.stringify(
            data.insights.sentiment_distribution
        );

        const keywords = data.insights.negative_common_keywords
            .map((p) => `${p[0]} (${p[1]})`)
            .join(", ");
        document.getElementById("negKeywords").textContent = keywords || "None";

        const insightsList = document.getElementById("insightsList");
        insightsList.innerHTML = "";
        data.insights.actionable_insights.forEach((text) => {
            const li = document.createElement("li");
            li.textContent = text;
            insightsList.appendChild(li);
        });

        // Reviews
        const reviewsList = document.getElementById("reviewsList");
        reviewsList.innerHTML = "";
        data.reviews_sample.forEach((review) => {
            const li = document.createElement("li");
            li.innerHTML = `<strong>${review.rating}★ ${review.title}</strong>: ${review.review}`;
            reviewsList.appendChild(li);
        });
    }
});
