#!/usr/bin/env python3
"""
Direct API test for LawBrain
"""
import requests
import json
import time

API_URL = "http://127.0.0.1:2024"

def test_lawbrain():
    print("🏛️  Testing LawBrain - AI Law Firm")
    print("=" * 60)

    # Create a thread
    thread_resp = requests.post(f"{API_URL}/threads", json={})
    thread_id = thread_resp.json()["thread_id"]
    print(f"✅ Created consultation session: {thread_id}\n")

    # Test question
    question = "I was arrested for DUI last night. What should I do?"

    print(f"{'='*60}")
    print(f"CLIENT: {question}")
    print(f"{'='*60}\n")

    # Send a run request (blocking)
    run_payload = {
        "assistant_id": "agent",
        "input": {"messages": [{"role": "user", "content": question}]},
    }

    run_resp = requests.post(
        f"{API_URL}/threads/{thread_id}/runs/wait",
        json=run_payload
    )

    if run_resp.status_code == 200:
        result = run_resp.json()
        print("🤖 LAW FIRM RESPONSE:\n")

        # Extract messages from the result
        if "values" in result and "messages" in result["values"]:
            for msg in result["values"]["messages"]:
                # Check if it's an AI message
                content = ""
                if isinstance(msg, dict):
                    if msg.get("type") == "ai" or msg.get("role") == "assistant":
                        content = msg.get("content", "")
                    elif "content" in msg:
                        content = msg.get("content", "")

                if content and content != question:  # Don't print the user's question back
                    print(f"{content}\n")
    else:
        print(f"Error: {run_resp.status_code}")
        print(run_resp.text)

if __name__ == "__main__":
    test_lawbrain()
