from typing import Dict

from fastapi import FastAPI, HTTPException
from loguru import logger
from pydantic import BaseModel

# Configure loguru
logger.remove()  # Remove default handler
logger.add(
    sink=lambda message: print(message, end=""),
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)

app = FastAPI(
    title="Sentiment Analysis API",
    description="A simple sentiment analysis API for CI/CD demonstration",
    version="1.0.18",
)


class TextInput(BaseModel):
    text: str


class PredictionResponse(BaseModel):
    text: str
    sentiment: str
    confidence: float


# Simple rule-based sentiment analysis (for demo purposes)
def predict_sentiment(text: str) -> Dict[str, any]:
    """
    Simple sentiment analysis using keyword matching.
    In a real project, this would load a trained model.
    """
    text_lower = text.lower()

    positive_words = [
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
    negative_words = [
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

    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)

    if positive_count > negative_count:
        sentiment = "positive"
        confidence = min(0.9, 0.6 + (positive_count - negative_count) * 0.1)
    elif negative_count > positive_count:
        sentiment = "negative"
        confidence = min(0.9, 0.6 + (negative_count - positive_count) * 0.1)
    else:
        sentiment = "neutral"
        confidence = 0.5

    return {"sentiment": sentiment, "confidence": round(confidence, 2)}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Sentiment Analysis API is running!", "status": "healthy"}


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {"status": "healthy", "service": "sentiment-api", "version": "1.0.0"}


@app.post("/predict", response_model=PredictionResponse)
async def predict(input_data: TextInput):
    """
    Predict sentiment for the given text
    """
    try:
        if not input_data.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        logger.info(f"Processing text: {input_data.text[:50]}...")

        prediction = predict_sentiment(input_data.text)

        response = PredictionResponse(
            text=input_data.text,
            sentiment=prediction["sentiment"],
            confidence=prediction["confidence"],
        )

        logger.info(
            f"Prediction: {prediction['sentiment']} (confidence: {prediction['confidence']})",
        )

        return response

    except Exception as e:
        logger.error(f"Error processing request: {e!s}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
