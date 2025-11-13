import os
import sys

import pytest
from fastapi.testclient import TestClient

# Add API directory to path for importing
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "api"))

try:
    from app import app

    client = TestClient(app)
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False


@pytest.mark.skipif(not API_AVAILABLE, reason="API app not available")
class TestAPI:
    """Test cases for the sentiment analysis API"""

    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["status"] == "healthy"

    def test_health_check(self):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "sentiment-api"

    def test_predict_positive(self):
        """Test prediction with positive text"""
        response = client.post(
            "/predict",
            json={"text": "I love this amazing product!"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment"] == "positive"
        assert data["confidence"] > 0.5
        assert data["text"] == "I love this amazing product!"

    def test_predict_negative(self):
        """Test prediction with negative text"""
        response = client.post("/predict", json={"text": "This is terrible and awful"})
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment"] == "negative"
        assert data["confidence"] > 0.5

    def test_predict_neutral(self):
        """Test prediction with neutral text"""
        response = client.post("/predict", json={"text": "This is a regular sentence"})
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment"] in ["neutral", "positive", "negative"]
        assert 0 <= data["confidence"] <= 1

    def test_empty_text(self):
        """Test with empty text"""
        response = client.post("/predict", json={"text": ""})
        assert response.status_code == 400

    def test_whitespace_text(self):
        """Test with whitespace only"""
        response = client.post("/predict", json={"text": "   "})
        assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__])
