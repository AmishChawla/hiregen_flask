#!/usr/bin/env python3
"""
Test script to verify the job posting flow works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot_agent import ChatbotAgent

def test_job_posting_flow():
    """Test the complete job posting flow"""
    
    # Initialize the chatbot
    chatbot = ChatbotAgent()
    
    # Mock user context
    user_context = {
        "user_id": "test_user_123",
        "user_role": "employer",
        "company": "TestCorp Inc."
    }
    
    print("🤖 Testing Job Posting Flow")
    print("=" * 50)
    
    # Test Case 1: User says "job title is chief"
    print("\n📝 Test Case 1: 'job title is chief'")
    print("-" * 40)
    
    response1 = chatbot.process_message("job title is chief", user_context)
    print(f"Response Type: {response1.get('type', 'unknown')}")
    print(f"Success: {response1.get('success', False)}")
    print(f"Has Message: {'message' in response1}")
    print(f"Has Content: {'content' in response1}")
    print(f"Content: {response1.get('content', 'No content')[:200]}...")
    
    # Test Case 2: User accepts suggestions
    print("\n📝 Test Case 2: User accepts suggestions")
    print("-" * 40)
    
    response2 = chatbot.process_message("accept", user_context)
    print(f"Response Type: {response2.get('type', 'unknown')}")
    print(f"Success: {response2.get('success', False)}")
    print(f"Has Message: {'message' in response2}")
    print(f"Has Content: {'content' in response2}")
    print(f"Content: {response2.get('content', 'No content')[:200]}...")
    
    # Test Case 3: User confirms final details
    print("\n📝 Test Case 3: User confirms final details")
    print("-" * 40)
    
    response3 = chatbot.process_message("yes", user_context)
    print(f"Response Type: {response3.get('type', 'unknown')}")
    print(f"Success: {response3.get('success', False)}")
    print(f"Has Message: {'message' in response3}")
    print(f"Has Content: {'content' in response3}")
    print(f"Content: {response3.get('content', 'No content')[:200]}...")

def test_job_title_extraction():
    """Test job title extraction"""
    
    chatbot = ChatbotAgent()
    
    test_cases = [
        "job title is chief",
        "I need a developer job",
        "Post a marketing manager position",
        "Hire a data analyst",
        "Looking for a customer service representative"
    ]
    
    print("\n🔍 Testing Job Title Extraction")
    print("=" * 50)
    
    for i, test_message in enumerate(test_cases, 1):
        extracted_title = chatbot.extract_job_title(test_message)
        print(f"Test {i}: '{test_message}' -> '{extracted_title}'")

def test_error_handling():
    """Test error handling and response format"""
    
    chatbot = ChatbotAgent()
    user_context = {"user_id": "test_user_123"}
    
    print("\n🔧 Testing Error Handling")
    print("=" * 50)
    
    # Test with invalid input
    response = chatbot.process_message("invalid input", user_context)
    print(f"Response Type: {response.get('type', 'unknown')}")
    print(f"Success: {response.get('success', False)}")
    print(f"Has Message: {'message' in response}")
    print(f"Has Content: {'content' in response}")
    print(f"Content: {response.get('content', 'No content')[:100]}...")

if __name__ == "__main__":
    print("🚀 Starting Job Posting Flow Tests...")
    
    try:
        test_job_title_extraction()
        test_error_handling()
        test_job_posting_flow()
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
