#!/usr/bin/env python3
"""Test if LangGraph API is accessible"""
import requests

print("Testing local API...")
try:
    response = requests.get("http://127.0.0.1:2024/ok")
    print(f"✅ Local API Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\nTesting /info endpoint...")
try:
    response = requests.get("http://127.0.0.1:2024/info")
    print(f"✅ Info Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\nTesting /assistants endpoint...")
try:
    response = requests.get("http://127.0.0.1:2024/assistants")
    print(f"✅ Assistants Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")
