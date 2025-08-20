import openai
import json
import datetime
from typing import Dict, Any, List
from flask_login import current_user
import api_calls

class JobPostingAgent:
    def __init__(self):
        self.conversation_state = {}
        
    def process_message(self, user_message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for processing user messages
        """
        try:
            # Ensure user_context is not None
            if user_context is None:
                user_context = {}
            
            user_id = user_context.get('user_id', 'default')
            current_state = self.conversation_state.get(user_id, {})
            
            print(f"DEBUG: Processing message: '{user_message}'")
            print(f"DEBUG: User ID: {user_id}")
            print(f"DEBUG: Current state: {current_state}")
            print(f"DEBUG: Full conversation state: {self.conversation_state}")
            
            # Check if we're in an active job posting flow
            if current_state.get('flow') == 'job_posting':
                print(f"DEBUG: Continuing job posting flow, step: {current_state.get('step')}")
                return self.handle_job_posting_flow(user_message, user_context, current_state)
            
            # Check if this is a job posting request
            if self.is_job_posting_request(user_message):
                print(f"DEBUG: Starting new job posting flow")
                # Start job posting flow
                new_state = {
                    'flow': 'job_posting',
                    'step': 'waiting_for_title'
                }
                self.conversation_state[user_id] = new_state
                print(f"DEBUG: Set new state: {new_state}")
                return self.handle_job_posting_flow(user_message, user_context, new_state)
            
            # Default response for non-job posting requests
            return {
                "type": "conversation",
                "message": "Hello! I'm your job posting assistant. I can help you create and post job openings with AI-powered suggestions. Just say 'Post a job' or 'Create a job posting' to get started!",
                "content": "Hello! I'm your job posting assistant. I can help you create and post job openings with AI-powered suggestions. Just say 'Post a job' or 'Create a job posting' to get started!",
                "success": True
            }
            
        except Exception as e:
            return {
                "type": "error",
                "message": f"I encountered an error: {str(e)}. Please try again.",
                "content": f"I encountered an error: {str(e)}. Please try again.",
                "success": False
            }
    
    def is_job_posting_request(self, user_message: str) -> bool:
        """
        Check if user wants to post a job
        """
        user_message_lower = user_message.lower()
        
        job_keywords = [
            'post a job', 'create job', 'new job', 'hire', 'job posting',
            'post job', 'create a job', 'job opening', 'recruit'
        ]
        
        return any(keyword in user_message_lower for keyword in job_keywords)
    
    def handle_job_posting_flow(self, user_message: str, user_context: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the job posting conversation flow
        """
        user_id = user_context.get('user_id', 'default')
        step = current_state.get('step', 'waiting_for_title')
        
        if step == 'waiting_for_title':
            return self.handle_job_title_step(user_message, user_context)
        elif step == 'waiting_for_accept_reject':
            return self.handle_suggestions_response(user_message, user_context)
        elif step == 'waiting_for_modifications':
            return self.handle_modifications(user_message, user_context)
        elif step == 'waiting_for_confirmation':
            return self.handle_final_confirmation(user_message, user_context)
        else:
            # Reset and start over
            self.conversation_state[user_id] = {'flow': 'job_posting', 'step': 'waiting_for_title'}
            return {
                "type": "prompt",
                "message": "Please provide the job title for the position you want to post.",
                "content": "Please provide the job title for the position you want to post.",
                "success": True
            }
    
    def handle_job_title_step(self, user_message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the job title input step
        """
        user_id = user_context.get('user_id', 'default')
        
        # Extract job title using OpenAI
        job_title = self.extract_job_title(user_message)
        
        if job_title:
            # Generate suggestions
            return self.generate_job_suggestions(job_title, user_context)
        else:
            return {
                "type": "prompt",
                "message": "Please provide the job title for the position you want to post. For example: 'Software Engineer', 'Marketing Manager', 'Customer Service Representative'",
                "content": "Please provide the job title for the position you want to post. For example: 'Software Engineer', 'Marketing Manager', 'Customer Service Representative'",
                "success": True
            }
    
    def extract_job_title(self, user_message: str) -> str:
        """
        Extract job title from user message using OpenAI
        """
        try:
            prompt = f"""Extract the job title from this user message. If no specific job title is mentioned, return an empty string.

User message: "{user_message}"

Examples:
- "I want to hire a software engineer" → "Software Engineer"
- "Post a job for marketing manager" → "Marketing Manager"
- "Create a job for data analyst" → "Data Analyst"
- "Post a new job" → ""
- "I need to hire someone" → ""

Return only the job title or empty string."""

            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Extract job titles from user messages."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=50
            )
            
            job_title = response.choices[0].message.content.strip()
            return job_title if job_title and job_title.lower() not in ['', 'none', 'n/a'] else ""
            
        except Exception as e:
            print(f"Error extracting job title: {e}")
            return ""
    
    def generate_job_suggestions(self, job_title: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate job suggestions using OpenAI
        """
        try:
            prompt = f"""Generate a complete job posting for the position: "{job_title}"

IMPORTANT: Return ONLY valid JSON without any additional text, quotes, or formatting.

{{
    "job_title": "{job_title}",
    "job_description": "Detailed job description (2-3 paragraphs)",
    "job_requirements": "Key requirements and qualifications",
    "job_benefits": "Attractive benefits package",
    "job_type": "Full Time",
    "work_style": "On-Site",
    "work_experience": "Mid-Level",
    "industry": "Relevant industry",
    "min_salary": "50000",
    "max_salary": "80000",
    "salary_currency": "$",
    "salary_time_unit": "per year",
    "address_city": "City name",
    "address_country": "Country name"
}}

Make the suggestions realistic, professional, and tailored to the job title. Use appropriate salary ranges and currency symbols. Return ONLY the JSON object, nothing else."""

            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional HR consultant. You must return ONLY valid JSON responses without any additional text, quotes, or formatting. Never include markdown, code blocks, or explanatory text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Debug: Print the raw response
            print(f"DEBUG: Raw AI response: {content}")
            
            # Clean JSON response
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            print(f"DEBUG: Cleaned content: {content}")
            
            try:
                suggestions = json.loads(content)
            except json.JSONDecodeError as e:
                # Try to extract JSON from the response using regex
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        suggestions = json.loads(json_match.group())
                    except:
                        # If still fails, return error
                        return {
                            "type": "error",
                            "message": f"❌ I couldn't parse the AI response. Please try again.",
                            "content": f"❌ I couldn't parse the AI response. Please try again.",
                            "success": False
                        }
                else:
                    return {
                        "type": "error",
                        "message": f"❌ I couldn't parse the AI response. Please try again.",
                        "content": f"❌ I couldn't parse the AI response. Please try again.",
                        "success": False
                    }
            
            # Store in conversation state
            user_id = user_context.get('user_id', 'default')
            new_state = {
                'flow': 'job_posting',
                'step': 'waiting_for_accept_reject',
                'job_title': job_title,
                'suggestions': suggestions
            }
            self.conversation_state[user_id] = new_state
            
            # Create suggestion message
            suggestion_message = f"""🤖 **I've generated suggestions for your "{job_title}" position:**

**Job Title:** {suggestions.get('job_title', job_title)}
**Job Type:** {suggestions.get('job_type', 'Full Time')}
**Work Style:** {suggestions.get('work_style', 'On-Site')}
**Experience Level:** {suggestions.get('work_experience', 'Mid-Level')}
**Industry:** {suggestions.get('industry', 'N/A')}
**Salary Range:** {suggestions.get('min_salary', 'N/A')} - {suggestions.get('max_salary', 'N/A')} {suggestions.get('salary_currency', '$')} {suggestions.get('salary_time_unit', 'per year')}
**Location:** {suggestions.get('address_city', 'N/A')}, {suggestions.get('address_country', 'N/A')}

**Job Description:**
{suggestions.get('job_description', 'N/A')}

**Requirements:**
{suggestions.get('job_requirements', 'N/A')}

**Benefits:**
{suggestions.get('job_benefits', 'N/A')}

**What would you like to do?**
1. ✅ **Accept these suggestions**
2. ✏️ **Modify some details**
3. 🔄 **Generate different suggestions**
4. ❌ **Cancel job posting**

Please respond with your choice (1, 2, 3, or 4)."""

            return {
                "type": "suggestions",
                "message": suggestion_message,
                "content": suggestion_message,
                "success": True
            }
            
        except Exception as e:
            return {
                "type": "error",
                "message": f"❌ I couldn't generate suggestions: {str(e)}. Please try again.",
                "content": f"❌ I couldn't generate suggestions: {str(e)}. Please try again.",
                "success": False
            }
    
    def handle_suggestions_response(self, user_message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle user response to suggestions
        """
        user_id = user_context.get('user_id', 'default')
        current_state = self.conversation_state.get(user_id, {})
        suggestions = current_state.get('suggestions', {})
        
        print(f"DEBUG: handle_suggestions_response - User message: '{user_message}'")
        print(f"DEBUG: handle_suggestions_response - Current state: {current_state}")
        print(f"DEBUG: handle_suggestions_response - Suggestions: {suggestions}")
        
        user_message_lower = user_message.lower().strip()
        
        # Check for accept
        if any(phrase in user_message_lower for phrase in ['accept', 'yes', '1', 'ok', 'good', 'approve']):
            # Get the actual suggestions from the current state
            suggestions = current_state.get('suggestions', {})
            print(f"DEBUG: Current state: {current_state}")
            print(f"DEBUG: Suggestions: {suggestions}")
            return self.show_final_confirmation(user_context, suggestions)
        
        # Check for modify
        elif any(phrase in user_message_lower for phrase in ['modify', 'change', 'edit', '2', 'update']):
            current_state['step'] = 'waiting_for_modifications'
            self.conversation_state[user_id] = current_state
            return {
                "type": "modify_prompt",
                "message": "What would you like to modify? You can say things like:\n• 'Change salary to $80,000-$100,000'\n• 'Make it remote work'\n• 'Change job type to part-time'\n• 'Update the requirements'\n• 'Change location to New York'\n\nPlease specify what you want to change:",
                "content": "What would you like to modify? You can say things like:\n• 'Change salary to $80,000-$100,000'\n• 'Make it remote work'\n• 'Change job type to part-time'\n• 'Update the requirements'\n• 'Change location to New York'\n\nPlease specify what you want to change:",
                "success": True
            }
        
        # Check for regenerate
        elif any(phrase in user_message_lower for phrase in ['regenerate', 'different', 'new', '3', 'generate']):
            return self.generate_job_suggestions(current_state.get('job_title', ''), user_context)
        
        # Check for cancel - be more specific to avoid false positives
        elif any(phrase in user_message_lower for phrase in ['cancel', 'stop', 'quit', '4']) or (user_message_lower.strip() == 'no' and len(user_message_lower.split()) == 1):
            self.conversation_state[user_id] = {}
            return {
                "type": "cancelled",
                "message": "❌ Job posting cancelled. How else can I help you?",
                "content": "❌ Job posting cancelled. How else can I help you?",
                "success": True
            }
        
        else:
            return {
                "type": "clarification",
                "message": "I'm not sure what you'd like to do. Please choose:\n1. ✅ Accept these suggestions\n2. ✏️ Modify some details\n3. 🔄 Generate different suggestions\n4. ❌ Cancel job posting",
                "content": "I'm not sure what you'd like to do. Please choose:\n1. ✅ Accept these suggestions\n2. ✏️ Modify some details\n3. 🔄 Generate different suggestions\n4. ❌ Cancel job posting",
                "success": True
            }
    
    def handle_modifications(self, user_message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle user modifications to suggestions
        """
        user_id = user_context.get('user_id', 'default')
        current_state = self.conversation_state.get(user_id, {})
        suggestions = current_state.get('suggestions', {})
        
        try:
            modification_prompt = f"""The user wants to modify their job posting suggestions.

Current suggestions:
{json.dumps(suggestions, indent=2)}

User modification request: "{user_message}"

Please update the suggestions based on the user's request. Return only the modified JSON object with the updated fields. Keep other fields unchanged unless specifically requested to modify them.

Return only valid JSON without any additional text."""

            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional HR consultant. Provide only valid JSON responses."},
                    {"role": "user", "content": modification_prompt}
                ],
                temperature=0.2,
                max_tokens=800
            )
            
            modified_suggestions = json.loads(response.choices[0].message.content)
            
            # Merge with existing suggestions
            updated_suggestions = {**suggestions, **modified_suggestions}
            
            # Update conversation state
            current_state['suggestions'] = updated_suggestions
            current_state['step'] = 'waiting_for_accept_reject'
            self.conversation_state[user_id] = current_state
            
            # Show updated suggestions
            suggestion_message = f"""✏️ **I've updated your job posting suggestions:**

**Job Title:** {updated_suggestions.get('job_title', 'N/A')}
**Job Type:** {updated_suggestions.get('job_type', 'Full Time')}
**Work Style:** {updated_suggestions.get('work_style', 'On-Site')}
**Experience Level:** {updated_suggestions.get('work_experience', 'Mid-Level')}
**Industry:** {updated_suggestions.get('industry', 'N/A')}
**Salary Range:** {updated_suggestions.get('min_salary', 'N/A')} - {updated_suggestions.get('max_salary', 'N/A')} {updated_suggestions.get('salary_currency', '$')} {updated_suggestions.get('salary_time_unit', 'per year')}
**Location:** {updated_suggestions.get('address_city', 'N/A')}, {updated_suggestions.get('address_country', 'N/A')}

**Job Description:**
{updated_suggestions.get('job_description', 'N/A')}

**Requirements:**
{updated_suggestions.get('job_requirements', 'N/A')}

**Benefits:**
{updated_suggestions.get('job_benefits', 'N/A')}

**What would you like to do?**
1. ✅ **Accept these suggestions**
2. ✏️ **Modify more details**
3. 🔄 **Generate different suggestions**
4. ❌ **Cancel job posting**

Please respond with your choice (1, 2, 3, or 4)."""

            return {
                "type": "suggestions",
                "message": suggestion_message,
                "content": suggestion_message,
                "success": True
            }
            
        except Exception as e:
            return {
                "type": "error",
                "message": f"❌ I couldn't modify the suggestions: {str(e)}. Please try again with clearer instructions.",
                "content": f"❌ I couldn't modify the suggestions: {str(e)}. Please try again with clearer instructions.",
                "success": False
            }
    
    def show_final_confirmation(self, user_context: Dict[str, Any], suggestions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Show final confirmation with all job details
        """
        user_id = user_context.get('user_id', 'default')
        
        # Update conversation state
        new_state = {
            'flow': 'job_posting',
            'step': 'waiting_for_confirmation',
            'final_job_details': suggestions
        }
        self.conversation_state[user_id] = new_state
        
        confirmation_message = f"""📋 **Final Job Details - Please Confirm:**

**Job Title:** {suggestions.get('job_title', 'N/A')}
**Job Type:** {suggestions.get('job_type', 'Full Time')}
**Work Style:** {suggestions.get('work_style', 'On-Site')}
**Experience Level:** {suggestions.get('work_experience', 'Mid-Level')}
**Industry:** {suggestions.get('industry', 'N/A')}
**Salary Range:** {suggestions.get('min_salary', 'N/A')} - {suggestions.get('max_salary', 'N/A')} {suggestions.get('salary_currency', '$')} {suggestions.get('salary_time_unit', 'per year')}
**Location:** {suggestions.get('address_city', 'N/A')}, {suggestions.get('address_country', 'N/A')}

**Job Description:**
{suggestions.get('job_description', 'N/A')}

**Requirements:**
{suggestions.get('job_requirements', 'N/A')}

**Benefits:**
{suggestions.get('job_benefits', 'N/A')}

**Are you ready to post this job?**
✅ **Yes, post the job**
❌ **No, let me make changes**

Please confirm with 'Yes' or 'No'."""

        return {
            "type": "confirmation",
            "message": confirmation_message,
            "content": confirmation_message,
            "success": True
        }
    
    def handle_final_confirmation(self, user_message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle final confirmation and post the job
        """
        user_id = user_context.get('user_id', 'default')
        current_state = self.conversation_state.get(user_id, {})
        job_details = current_state.get('final_job_details', {})
        
        user_message_lower = user_message.lower().strip()
        
        if any(phrase in user_message_lower for phrase in ['yes', 'confirm', 'post', 'ok', 'go ahead', 'proceed']):
            # Post the job
            result = self.post_job(job_details, user_context)
            
            # Clear conversation state
            self.conversation_state[user_id] = {}
            
            return result
        
        elif any(phrase in user_message_lower for phrase in ['no', 'change', 'modify', 'edit', 'back']):
            # Go back to modification step
            new_state = {
                'flow': 'job_posting',
                'step': 'waiting_for_accept_reject',
                'suggestions': job_details
            }
            self.conversation_state[user_id] = new_state
            
            return {
                "type": "modify_prompt",
                "message": "What would you like to modify? You can say things like:\n• 'Change salary to $80,000-$100,000'\n• 'Make it remote work'\n• 'Change job type to part-time'\n• 'Update the requirements'\n\nPlease specify what you want to change:",
                "content": "What would you like to modify? You can say things like:\n• 'Change salary to $80,000-$100,000'\n• 'Make it remote work'\n• 'Change job type to part-time'\n• 'Update the requirements'\n\nPlease specify what you want to change:",
                "success": True
            }
        
        else:
            return {
                "type": "clarification",
                "message": "Please confirm with 'Yes' to post the job or 'No' to make changes.",
                "content": "Please confirm with 'Yes' to post the job or 'No' to make changes.",
                "success": True
            }
    
    def post_job(self, job_details: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post the job using the API
        """
        try:
            # Calculate dates
            today = datetime.date.today()
            target_date = today + datetime.timedelta(days=30)
            
            # Prepare job details for API
            api_job_details = {
                "job_title": job_details.get("job_title", ""),
                "job_description": job_details.get("job_description", ""),
                "job_requirements": job_details.get("job_requirements", ""),
                "job_benefits": job_details.get("job_benefits", ""),
                "job_type": job_details.get("job_type", "Full Time"),
                "job_skills": "",
                "work_style": job_details.get("work_style", "On-Site"),
                "work_experience": job_details.get("work_experience", "Mid-Level"),
                "industry": job_details.get("industry", ""),
                "min_salary": float(job_details.get("min_salary")) if job_details.get("min_salary") else None,
                "max_salary": float(job_details.get("max_salary")) if job_details.get("max_salary") else None,
                "salary_currency": job_details.get("salary_currency", "$"),
                "salary_time_unit": job_details.get("salary_time_unit", "per year"),
                "address_city": job_details.get("address_city", ""),
                "address_country": job_details.get("address_country", ""),
                "address_province": "",
                "address_postal_code": "",
                "target_date": str(target_date.strftime("%Y-%m-%d")),
                "opening_date": str(today.strftime("%Y-%m-%d")),
                "job_opening_status": "Active",
                "status": "published"
            }

            # Call API to create job
            access_token = getattr(current_user, 'id', 'default') if current_user else 'default'
            result = api_calls.create_job_opening(
                job_detail=api_job_details,
                access_token=access_token
            )
            
            if result and isinstance(result, dict):
                return {
                    "type": "success",
                    "message": f"✅ Job '{job_details.get('job_title')}' has been successfully posted! The job is now live and accepting applications.",
                    "content": f"✅ Job '{job_details.get('job_title')}' has been successfully posted! The job is now live and accepting applications.",
                    "data": {"job_id": result.get("id") if result else None},
                    "success": True
                }
            else:
                return {
                    "type": "error",
                    "message": "❌ Failed to create job posting. Please try again or contact support.",
                    "content": "❌ Failed to create job posting. Please try again or contact support.",
                    "success": False
                }
                
        except Exception as e:
            return {
                "type": "error",
                "message": f"❌ Error creating job posting: {str(e)}",
                "content": f"❌ Error creating job posting: {str(e)}",
                "success": False
            } 