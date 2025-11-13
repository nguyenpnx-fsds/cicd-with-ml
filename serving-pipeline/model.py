from typing import Any, Dict

import kserve
from kserve import Model


class SentimentModel(Model):
    """
    Simple KServe-compatible sentiment analysis model
    This demonstrates how to create a custom Python model for KServe
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.ready = False

        # Simple sentiment analysis dictionaries
        self.positive_words = [
            "good",
            "great",
            "excellent",
            "amazing",
            "wonderful",
            "fantastic",
            "awesome",
            "love",
            "like",
            "happy",
            "joy",
        ]
        self.negative_words = [
            "bad",
            "terrible",
            "awful",
            "horrible",
            "hate",
            "dislike",
            "sad",
            "angry",
            "disappointed",
            "worst",
        ]

    def load(self):
        """Load the model - in this case, just set ready flag"""
        print("Loading sentiment analysis model...")
        self.ready = True
        print("Model loaded successfully!")

    def predict(self, payload: Dict, headers: Dict[str, str] = None) -> Dict:
        """
        Predict sentiment for the given text

        Args:
            payload: Input data containing 'instances' with text data
            headers: Request headers (optional)

        Returns:
            Dictionary with predictions
        """
        # Extract instances from payload
        instances = payload.get("instances", [])

        if not instances:
            return {"predictions": []}

        predictions = []

        for instance in instances:
            # Handle different input formats
            if isinstance(instance, str):
                text = instance
            elif isinstance(instance, dict):
                text = instance.get("text", instance.get("data", ""))
            else:
                text = str(instance)

            # Perform sentiment analysis
            result = self._analyze_sentiment(text)
            predictions.append(result)

        return {"predictions": predictions}

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Simple rule-based sentiment analysis
        """
        if not text or not text.strip():
            return {
                "text": text,
                "sentiment": "neutral",
                "confidence": 0.0,
                "error": "Empty text provided",
            }

        text_lower = text.lower()

        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)

        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.9, 0.6 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.9, 0.6 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = "neutral"
            confidence = 0.5

        return {
            "text": text,
            "sentiment": sentiment,
            "confidence": round(confidence, 2),
        }


if __name__ == "__main__":
    # Create and start the model server
    model = SentimentModel("sentiment-model")
    model.load()

    # Start KServe model server
    kserve.ModelServer().start([model])
