#!/usr/bin/env python3
"""
Simple test for LawBrain using LangGraph SDK
"""
from langgraph_sdk import get_client

def main():
    # Connect to the local LangGraph server
    client = get_client(url="http://127.0.0.1:2024")

    print("🏛️  Testing LawBrain - AI Law Firm")
    print("=" * 60)

    # Create an assistant
    assistant = client.assistants.get("agent")
    print(f"✅ Connected to: {assistant['graph_id']}\n")

    # Create a thread
    thread = client.threads.create()
    print(f"✅ Created consultation session: {thread['thread_id']}\n")

    # Test case
    question = "I was arrested for DUI last night. What should I do?"

    print(f"{'='*60}")
    print(f"CLIENT: {question}")
    print(f"{'='*60}\n")

    # Run the assistant
    run = client.runs.create(
        thread_id=thread["thread_id"],
        assistant_id="agent",
        input={"messages": [{"role": "user", "content": question}]}
    )

    # Wait for completion
    client.runs.join(thread_id=thread["thread_id"], run_id=run["run_id"])

    # Get the response
    state = client.threads.get_state(thread_id=thread["thread_id"])

    # Print the AI's response
    if state and "values" in state and "messages" in state["values"]:
        messages = state["values"]["messages"]
        for msg in messages:
            if msg.get("type") == "ai" or msg.get("role") == "assistant":
                print(f"🤖 LAW FIRM: {msg.get('content', '')}\n")

if __name__ == "__main__":
    main()
