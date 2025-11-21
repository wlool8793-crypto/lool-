#!/usr/bin/env python3
"""
Test script for LawBrain AI Law Firm
"""
import requests
import json
import time

API_URL = "http://127.0.0.1:2024"

def create_thread():
    """Create a new thread"""
    response = requests.post(f"{API_URL}/threads", json={})
    return response.json()["thread_id"]

def send_message(thread_id, message):
    """Send a message to the law firm"""
    payload = {
        "input": {
            "messages": [{"role": "user", "content": message}]
        }
    }

    print(f"\n{'='*60}")
    print(f"CLIENT: {message}")
    print(f"{'='*60}\n")

    response = requests.post(
        f"{API_URL}/threads/{thread_id}/runs/stream",
        json=payload,
        headers={"Accept": "text/event-stream"},
        stream=True
    )

    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    if data[0] == "data":
                        event_data = data[1]
                        # Print agent messages
                        if "messages" in event_data:
                            for msg in event_data["messages"]:
                                if hasattr(msg, "content"):
                                    content = msg.content
                                elif isinstance(msg, dict) and "content" in msg:
                                    content = msg["content"]
                                else:
                                    continue

                                if content and content.strip():
                                    print(f"🤖 {content}\n")
                except:
                    pass

def main():
    print("🏛️  Welcome to LawBrain - AI Law Firm")
    print("=" * 60)

    # Create a thread
    thread_id = create_thread()
    print(f"✅ Created consultation session: {thread_id}\n")

    # Test cases
    test_cases = [
        "I was arrested for DUI last night. What should I do?",
        "I want to start a tech startup. What legal steps do I need to take?",
        "I need help with a divorce and my spouse and I own a business together.",
    ]

    for case in test_cases:
        send_message(thread_id, case)
        time.sleep(1)  # Brief pause between cases

if __name__ == "__main__":
    main()
