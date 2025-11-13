#!/usr/bin/env python3
"""
Simple test script for KServe sentiment model
This demonstrates how to send requests to the deployed KServe model
"""

import time

import requests


def test_kserve_model(base_url: str = "http://localhost:8080"):
    """
    Test the KServe sentiment model with sample data

    Args:
        base_url: Base URL of the KServe model service
    """

    # KServe prediction endpoint
    predict_url = f"{base_url}/v1/models/sentiment-model:predict"

    # Test data - KServe expects 'instances' format
    test_cases = [
        {"instances": ["This is a great product!"]},
        {"instances": ["I hate this terrible service"]},
        {"instances": ["The weather is okay today"]},
        {
            "instances": [
                "I love this amazing feature!",
                "This is the worst experience ever",
                "Not bad, could be better",
            ]
        },
    ]

    print("Testing KServe Sentiment Model")
    print("=" * 50)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Input: {test_case['instances']}")

        try:
            response = requests.post(
                predict_url,
                json=test_case,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                predictions = result.get("predictions", [])

                for j, prediction in enumerate(predictions):
                    text = test_case["instances"][j]
                    sentiment = prediction.get("sentiment", "unknown")
                    confidence = prediction.get("confidence", 0.0)
                    print(f"  Text: '{text}'")
                    print(f"  Sentiment: {sentiment} (confidence: {confidence})")
            else:
                print(f"  Error: HTTP {response.status_code}")
                print(f"  Response: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"  Request failed: {e}")

        # Small delay between requests
        time.sleep(0.5)


def check_model_health(base_url: str = "http://localhost:8080"):
    """
    Check if the KServe model is healthy and ready
    """
    health_url = f"{base_url}/v1/models/sentiment-model"

    try:
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            model_info = response.json()
            print("Model Status:")
            print(f"  Name: {model_info.get('name', 'unknown')}")
            print(f"  Ready: {model_info.get('ready', False)}")
            return True
        else:
            print(f"Health check failed: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Health check failed: {e}")
        return False


if __name__ == "__main__":
    import sys

    # Get base URL from command line argument or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"

    print(f"Testing KServe model at: {base_url}")

    # First check if model is healthy
    print("\nChecking model health...")
    if check_model_health(base_url):
        print("Model is healthy! Running tests...\n")
        test_kserve_model(base_url)
    else:
        print("Model is not ready. Please check the deployment.")
        sys.exit(1)
