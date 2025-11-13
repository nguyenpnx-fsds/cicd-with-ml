import json
import os
import pickle
from datetime import datetime
from typing import Dict, List, Tuple

from loguru import logger

# Configure loguru
logger.remove()  # Remove default handler
logger.add(
    sink=lambda message: print(message, end=""),
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)


class SimpleModelTrainer:
    """
    A simple sentiment analysis model trainer for demonstration purposes.
    In a real project, this would use scikit-learn, transformers, or other ML libraries.
    """

    def __init__(self):
        self.model_data = None
        self.training_stats = {}

    def generate_sample_data(self) -> List[Tuple[str, str]]:
        """Generate sample training data"""
        sample_data = [
            ("I love this product!", "positive"),
            ("This is amazing work", "positive"),
            ("Great job on the project", "positive"),
            ("Excellent quality and service", "positive"),
            ("I'm very happy with this", "positive"),
            ("Wonderful experience overall", "positive"),
            ("This is terrible", "negative"),
            ("I hate this so much", "negative"),
            ("Worst experience ever", "negative"),
            ("Very disappointed with quality", "negative"),
            ("This is awful and bad", "negative"),
            ("I don't like this at all", "negative"),
            ("It's okay I guess", "neutral"),
            ("This is average", "neutral"),
            ("Nothing special about it", "neutral"),
            ("Could be better or worse", "neutral"),
        ]

        # Add some random variations
        additional_positive = [
            "Fantastic results!",
            "Outstanding performance",
            "Incredible work",
            "Absolutely brilliant",
            "Superb quality",
            "Marvelous experience",
        ]
        additional_negative = [
            "Complete disaster",
            "Total failure",
            "Absolutely horrible",
            "Completely useless",
            "Worst possible outcome",
            "Extremely poor",
        ]

        sample_data.extend([(text, "positive") for text in additional_positive])
        sample_data.extend([(text, "negative") for text in additional_negative])

        return sample_data

    def extract_features(self, data: List[Tuple[str, str]]) -> Dict:
        """Extract simple features from training data"""
        positive_words = set()
        negative_words = set()

        for text, label in data:
            words = text.lower().split()
            if label == "positive":
                positive_words.update(words)
            elif label == "negative":
                negative_words.update(words)

        # Remove common words that appear in both
        common_words = positive_words & negative_words
        positive_words -= common_words
        negative_words -= common_words

        return {
            "positive_words": list(positive_words),
            "negative_words": list(negative_words),
            "common_words": list(common_words),
        }

    def train_model(self) -> Dict:
        """Train the sentiment analysis model"""
        logger.info("Starting model training...")

        # Generate training data
        training_data = self.generate_sample_data()
        logger.info(f"Generated {len(training_data)} training samples")

        # Extract features
        features = self.extract_features(training_data)
        logger.info(
            f"Extracted {len(features['positive_words'])} positive words and {len(features['negative_words'])} negative words",
        )

        # Create model (simple word-based classifier)
        self.model_data = {
            "positive_words": features["positive_words"],
            "negative_words": features["negative_words"],
            "training_size": len(training_data),
            "trained_at": datetime.now().isoformat(),
            "version": "1.0.0",
        }

        # Calculate simple training stats
        self.training_stats = {
            "total_samples": len(training_data),
            "positive_samples": len([x for x in training_data if x[1] == "positive"]),
            "negative_samples": len([x for x in training_data if x[1] == "negative"]),
            "neutral_samples": len([x for x in training_data if x[1] == "neutral"]),
            "feature_count": len(features["positive_words"])
            + len(features["negative_words"]),
            "training_time": datetime.now().isoformat(),
        }

        logger.info("Model training completed successfully!")
        return self.model_data

    def save_model(self, model_dir: str = "../models"):
        """Save the trained model"""
        os.makedirs(model_dir, exist_ok=True)

        model_path = os.path.join(model_dir, "sentiment_model.pkl")
        stats_path = os.path.join(model_dir, "training_stats.json")

        # Save model
        with open(model_path, "wb") as f:
            pickle.dump(self.model_data, f)

        # Save training stats
        with open(stats_path, "w") as f:
            json.dump(self.training_stats, f, indent=2)

        logger.info(f"Model saved to {model_path}")
        logger.info(f"Training stats saved to {stats_path}")

        return model_path, stats_path

    def validate_model(self) -> Dict:
        """Simple model validation"""
        if not self.model_data:
            raise ValueError("Model not trained yet!")

        # Simple validation with test cases
        test_cases = [
            ("This is great!", "positive"),
            ("I love it", "positive"),
            ("This is terrible", "negative"),
            ("I hate this", "negative"),
        ]

        correct = 0
        for text, expected in test_cases:
            predicted = self._predict_single(text)
            if predicted == expected:
                correct += 1

        accuracy = correct / len(test_cases)

        validation_results = {
            "accuracy": accuracy,
            "correct_predictions": correct,
            "total_test_cases": len(test_cases),
            "validation_time": datetime.now().isoformat(),
        }

        logger.info(f"Model validation completed. Accuracy: {accuracy:.2%}")
        return validation_results

    def _predict_single(self, text: str) -> str:
        """Simple prediction for validation"""
        if not self.model_data:
            return "neutral"

        text_lower = text.lower()
        positive_count = sum(
            1 for word in self.model_data["positive_words"] if word in text_lower
        )
        negative_count = sum(
            1 for word in self.model_data["negative_words"] if word in text_lower
        )

        if positive_count > negative_count:
            return "positive"
        if negative_count > positive_count:
            return "negative"
        return "neutral"


def main():
    """Main training pipeline"""
    logger.info("Starting sentiment analysis model training pipeline...")

    try:
        # Initialize trainer
        trainer = SimpleModelTrainer()

        # Train model
        trainer.train_model()

        # Validate model
        validation_results = trainer.validate_model()

        # Save model
        model_path, stats_path = trainer.save_model()

        # Print summary
        logger.info("=" * 50)
        logger.info("TRAINING PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info("=" * 50)
        logger.info(f"Model saved to: {model_path}")
        logger.info(f"Training stats: {stats_path}")
        logger.info(f"Validation accuracy: {validation_results['accuracy']:.2%}")
        logger.info(f"Training samples: {trainer.training_stats['total_samples']}")
        logger.info("=" * 50)

        return True

    except Exception as e:
        logger.error(f"Training pipeline failed: {e!s}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
