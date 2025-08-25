#!/usr/bin/env python3
"""
Test script for the AI Chat Agent
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_chat_agent import AIChatAgent
import json

def test_ai_chat_agent():
    """Test the AI chat agent with natural conversation"""
    
    print("🤖 Testing AI Chat Agent")
    print("=" * 50)
    
    # Initialize agent
    agent = AIChatAgent()
    
    # Test session
    user_id = "test_user_123"
    session_id = "test_session_456"
    
    # Test natural conversation flow
    test_messages = [
        "Hi, I need help creating a job posting",
        "I want to hire a software engineer",
        "Can you make it remote work?",
        "Change the salary to $100,000-$150,000",
        "Yes, I'm ready to post this job"
    ]
    
    print(f"User ID: {user_id}")
    print(f"Session ID: {session_id}")
    print()
    
    for i, message in enumerate(test_messages, 1):
        print(f"📝 Message {i}: {message}")
        print("-" * 30)
        
        # Process message
        result = agent.process_message(message, user_id, session_id)
        
        if result['success']:
            print(f"✅ Success")
            print(f"🤖 Response: {result['message'][:100]}...")
            
            if result.get('job_details'):
                print(f"📋 Job Details: {result['job_details']['job_title']}")
                print(f"💰 Salary: {result['job_details']['min_salary']} - {result['job_details']['max_salary']} {result['job_details']['salary_currency']}")
                print(f"🏢 Industry: {result['job_details']['industry']}")
            
            if result.get('ready_to_post'):
                print("🚀 Job is ready to post!")
        else:
            print(f"❌ Error: {result['message']}")
        
        print()
    
    # Test job details retrieval
    print("🔍 Testing job details retrieval...")
    job_details = agent.get_job_details_for_posting(session_id)
    
    if job_details:
        print("✅ Job details retrieved successfully")
        print(f"📋 Job Title: {job_details['job_title']}")
        print(f"📝 Description: {job_details['job_description'][:100]}...")
        print(f"🎯 Status: {job_details['job_opening_status']}")
    else:
        print("❌ No job details found")
    
    print()
    print("🧹 Cleaning up...")
    agent.clear_conversation(session_id)
    print("✅ Test completed!")

def test_different_conversation():
    """Test a different conversation flow"""
    
    print("\n🔄 Testing Different Conversation Flow")
    print("=" * 50)
    
    agent = AIChatAgent()
    user_id = "test_user_789"
    session_id = "test_session_101"
    
    # Different conversation
    messages = [
        "Hello! Can you help me post a job?",
        "I need a marketing manager position",
        "Make it a part-time role",
        "Set the location to New York",
        "Perfect, let's post it"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"📝 Message {i}: {message}")
        
        result = agent.process_message(message, user_id, session_id)
        
        if result['success']:
            print(f"✅ Response: {result['message'][:80]}...")
            if result.get('ready_to_post'):
                print("🚀 Ready to post!")
        else:
            print(f"❌ Error: {result['message']}")
        
        print()
    
    agent.clear_conversation(session_id)

def test_get_user_jobs():
    """Test the get_user_jobs functionality"""
    print("\n" + "="*50)
    print("TESTING GET USER JOBS FUNCTIONALITY")
    print("="*50)
    
    agent = AIChatAgent()
    
    # Test conversation flow for viewing jobs
    test_messages = [
        "Hi, I want to see my existing job postings",
        "Show me my jobs",
        "What jobs have I posted?",
        "Can you list my current job openings?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Test {i}: '{message}' ---")
        
        result = agent.process_message(
            message=message,
            user_id="test_user_123",
            session_id="test_session_view_jobs"
        )
        
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        print(f"Fetch User Jobs: {result.get('fetch_user_jobs')}")
        print(f"Maximum Posts: {result.get('maximum_posts')}")
        
        if result.get('fetch_user_jobs'):
            print("✅ AI correctly identified intent to view user jobs!")
        else:
            print("❌ AI did not identify intent to view user jobs")

if __name__ == "__main__":
    test_ai_chat_agent()
    test_different_conversation()
    test_get_user_jobs()
