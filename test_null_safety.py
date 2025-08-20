#!/usr/bin/env python3
"""
Test script to verify null safety fixes in the chatbot
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot_agent import ChatbotAgent

def test_null_safety():
    """Test that the chatbot handles None values safely"""
    
    # Initialize the chatbot
    chatbot = ChatbotAgent()
    
    print("🔧 Testing Null Safety")
    print("=" * 50)
    
    # Test Case 1: None user_context
    print("\n📝 Test Case 1: None user_context")
    print("-" * 40)
    
    try:
        response1 = chatbot.process_message("Post a new job", None)
        print(f"✅ Success: {response1.get('success', False)}")
        print(f"Response Type: {response1.get('type', 'unknown')}")
        print(f"Content: {response1.get('content', 'No content')[:100]}...")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test Case 2: Empty user_context
    print("\n📝 Test Case 2: Empty user_context")
    print("-" * 40)
    
    try:
        response2 = chatbot.process_message("job title is chief", {})
        print(f"✅ Success: {response2.get('success', False)}")
        print(f"Response Type: {response2.get('type', 'unknown')}")
        print(f"Content: {response2.get('content', 'No content')[:100]}...")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test Case 3: Job posting keywords
    print("\n📝 Test Case 3: Job posting keywords")
    print("-" * 40)
    
    test_messages = [
        "Post a new job",
        "I need a developer",
        "Hire a manager",
        "Create a job posting"
    ]
    
    for i, message in enumerate(test_messages, 1):
        try:
            response = chatbot.process_message(message, None)
            print(f"Test {i}: '{message}' -> Success: {response.get('success', False)}")
        except Exception as e:
            print(f"Test {i}: '{message}' -> Error: {str(e)}")

def test_job_title_extraction():
    """Test job title extraction with null safety"""
    
    chatbot = ChatbotAgent()
    
    print("\n🔍 Testing Job Title Extraction with Null Safety")
    print("=" * 50)
    
    test_cases = [
        "job title is chief",
        "I need a developer job",
        "Post a marketing manager position",
        "Hire a data analyst",
        "Looking for a customer service representative"
    ]
    
    for i, test_message in enumerate(test_cases, 1):
        try:
            extracted_title = chatbot.extract_job_title(test_message)
            print(f"Test {i}: '{test_message}' -> '{extracted_title}'")
        except Exception as e:
            print(f"Test {i}: '{test_message}' -> Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Null Safety Tests...")
    
    try:
        test_null_safety()
        test_job_title_extraction()
        print("\n✅ All null safety tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
