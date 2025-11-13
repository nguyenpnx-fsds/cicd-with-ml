import json
import os
import pickle
import sys

import pytest

# Add training-pipeline directory to path for importing
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "training-pipeline"))

try:
    from train_model import SimpleModelTrainer

    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False


@pytest.mark.skipif(not PIPELINE_AVAILABLE, reason="Training pipeline not available")
class TestDataPipeline:
    """Test cases for the training pipeline"""

    def test_model_trainer_initialization(self):
        """Test that model trainer initializes correctly"""
        trainer = SimpleModelTrainer()
        assert trainer.model_data is None
        assert trainer.training_stats == {}

    def test_sample_data_generation(self):
        """Test sample data generation"""
        trainer = SimpleModelTrainer()
        data = trainer.generate_sample_data()

        assert len(data) > 0
        assert all(len(item) == 2 for item in data)  # Each item should be (text, label)

        labels = [item[1] for item in data]
        assert "positive" in labels
        assert "negative" in labels
        assert "neutral" in labels

    def test_feature_extraction(self):
        """Test feature extraction"""
        trainer = SimpleModelTrainer()
        sample_data = [
            ("I love this", "positive"),
            ("This is great", "positive"),
            ("I hate this", "negative"),
            ("This is terrible", "negative"),
        ]

        features = trainer.extract_features(sample_data)

        assert "positive_words" in features
        assert "negative_words" in features
        assert "common_words" in features
        assert isinstance(features["positive_words"], list)
        assert isinstance(features["negative_words"], list)

    def test_model_training(self):
        """Test model training process"""
        trainer = SimpleModelTrainer()
        model_data = trainer.train_model()

        assert model_data is not None
        assert "positive_words" in model_data
        assert "negative_words" in model_data
        assert "training_size" in model_data
        assert "trained_at" in model_data
        assert "version" in model_data

        # Check that training stats were updated
        assert trainer.training_stats["total_samples"] > 0
        assert "training_time" in trainer.training_stats

    def test_model_validation(self):
        """Test model validation"""
        trainer = SimpleModelTrainer()
        trainer.train_model()

        validation_results = trainer.validate_model()

        assert "accuracy" in validation_results
        assert "correct_predictions" in validation_results
        assert "total_test_cases" in validation_results
        assert "validation_time" in validation_results

        assert 0 <= validation_results["accuracy"] <= 1
        assert (
            validation_results["correct_predictions"]
            <= validation_results["total_test_cases"]
        )

    def test_model_save_and_load(self, tmp_path):
        """Test model saving and loading"""
        trainer = SimpleModelTrainer()
        trainer.train_model()

        # Save model to temporary directory
        model_path, stats_path = trainer.save_model(str(tmp_path))

        # Check files exist
        assert os.path.exists(model_path)
        assert os.path.exists(stats_path)

        # Load and verify model
        with open(model_path, "rb") as f:
            loaded_model = pickle.load(f)

        assert loaded_model["version"] == trainer.model_data["version"]
        assert loaded_model["positive_words"] == trainer.model_data["positive_words"]

        # Load and verify stats
        with open(stats_path) as f:
            loaded_stats = json.load(f)

        assert loaded_stats["total_samples"] == trainer.training_stats["total_samples"]


if __name__ == "__main__":
    pytest.main([__file__])
