#!/usr/bin/env python3
"""
Test authentication with Google Cloud Vertex AI
"""
import os
from langchain_google_vertexai import ChatVertexAI

# Set your project ID
PROJECT_ID = "lool-471716"
LOCATION = "us-central1"

print("🔍 Testing Google Cloud Vertex AI Authentication\n")
print(f"Project ID: {PROJECT_ID}")
print(f"Location: {LOCATION}\n")

try:
    # Try to initialize the model
    print("Initializing ChatVertexAI...")
    model = ChatVertexAI(
        model="gemini-2.5-pro",
        project=PROJECT_ID,
        location=LOCATION,
        temperature=0,
        max_retries=3
    )

    print("✅ Model initialized successfully!\n")

    # Try a simple test
    print("Testing with a simple question...")
    response = model.invoke("Say 'Hello from LawBrain!'")

    print(f"✅ Response received: {response.content}\n")
    print("🎉 Authentication is working perfectly!")

except Exception as e:
    print(f"❌ Error: {e}\n")
    print("Authentication failed. Please check:\n")
    print("1. Have you run: gcloud auth application-default login")
    print("2. Or set GOOGLE_APPLICATION_CREDENTIALS to your service account JSON")
    print("3. Is Vertex AI API enabled? https://console.cloud.google.com/apis/library/aiplatform.googleapis.com?project=lool-471716")
    print("\nSee SETUP_AUTH.md for detailed instructions.")
