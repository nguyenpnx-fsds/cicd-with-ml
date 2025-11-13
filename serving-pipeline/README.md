# Serving Pipeline for Sentiment Analysis

This directory contains the KServe deployment configuration for the sentiment analysis model.

## Files Overview

- `model.py` - Custom Python model implementation for KServe
- `requirements.txt` - Python dependencies for the model
- `Dockerfile` - Container image definition
- `inference-service.yaml` - KServe InferenceService definition
- `namespace.yaml` - Kubernetes namespace for organization
- `test_kserve.py` - Test script to verify the deployment

## Simple Usage

1. **Build the model image** (handled by Jenkins)
2. **Deploy to Kubernetes** with KServe InferenceService in the `ml-models` namespace
3. **Test the model** using the provided test script

**Manual deployment:**
```bash
kubectl apply -f namespace.yaml
kubectl apply -f inference-service.yaml
kubectl port-forward service/sentiment-model-predictor-default -n ml-models 8080:80
```

## Model API

The deployed model expects POST requests to `/v1/models/sentiment-model:predict` with:

```json
{
  "instances": ["Text to analyze"]
}
```

Response format:
```json
{
  "predictions": [
    {
      "text": "Text to analyze",
      "sentiment": "positive",
      "confidence": 0.8
    }
  ]
}
```

## Testing

Use the test script to verify your deployment:

```bash
python test_kserve.py http://your-kserve-endpoint
```
