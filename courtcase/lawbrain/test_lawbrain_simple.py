#!/usr/bin/env python3
"""
Simple test script to interact with LawBrain
"""
from agent import app

def test_lawbrain(question: str):
    """Test LawBrain with a legal question"""
    print(f"\n{'='*60}")
    print(f"CLIENT QUESTION: {question}")
    print(f"{'='*60}\n")

    # Invoke the law firm
    result = app.invoke({"messages": [("user", question)]})

    # Extract and print the response
    if result and "messages" in result:
        messages = result["messages"]
        print(f"RESPONSE FROM LAWBRAIN:\n")
        for msg in messages:
            if hasattr(msg, 'content'):
                print(f"{msg.content}\n")
            elif isinstance(msg, dict) and 'content' in msg:
                print(f"{msg['content']}\n")

    print(f"{'='*60}\n")
    return result

if __name__ == "__main__":
    # Test with different legal questions

    print("\n🧠 LAWBRAIN - AI Law Firm Test\n")

    # Test 1: Criminal Law
    test_lawbrain("I was arrested for DUI. What should I do?")

    # Test 2: Corporate Law
    # test_lawbrain("I want to start an LLC for my tech startup. What do I need to know?")

    # Test 3: Family Law
    # test_lawbrain("I'm considering divorce. What are my options?")
