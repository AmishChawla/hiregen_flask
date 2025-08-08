import openai
import json
import constants
from typing import Dict, Any, List
from flask_login import current_user
import api_calls
import datetime

class ChatbotAgent:
    def __init__(self):
        self.available_actions = {
            "post_job": self.post_job_action,
            "view_applications": self.view_applications_action,
            "manage_jobs": self.manage_jobs_action,
            "view_analytics": self.view_analytics_action,
            "help": self.help_action,
            "create_form": self.create_form_action,
            "manage_pages": self.manage_pages_action
        }
        
        # Define available functions for OpenAI
        self.functions = [
            {
                "name": "post_job",
                "description": "Create a new job posting on the user's account",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "job_title": {"type": "string", "description": "Title of the job position"},
                        "job_description": {"type": "string", "description": "Detailed description of the job"},
                        "job_requirements": {"type": "string", "description": "Requirements for the position"},
                        "job_benefits": {"type": "string", "description": "Benefits offered"},
                        "job_type": {"type": "string", "enum": ["Full Time", "Part Time", "Training", "Freelance", "Seasonal", "Contract", "Temporary"]},
                        "work_style": {"type": "string", "enum": ["On-Site", "Hybrid", "Remote"]},
                        "work_experience": {"type": "string", "enum": ["Fresher/Graduate", "Junior", "Mid-Level", "Senior", "Expert"]},
                        "industry": {"type": "string", "description": "Industry for the job"},
                        "min_salary": {"type": "string", "description": "Minimum salary"},
                        "max_salary": {"type": "string", "description": "Maximum salary"},
                        "salary_currency": {"type": "string", "description": "Salary currency"},
                        "salary_time_unit": {"type": "string", "description": "Salary time unit"},
                        "address_city": {"type": "string", "description": "City location"},
                        "address_country": {"type": "string", "description": "Country location"},
                        "target_date": {"type": "string", "description": "Target hiring date (YYYY-MM-DD)"}
                    },
                    "required": ["job_title", "job_description"]
                }
            },
            {
                "name": "view_applications",
                "description": "View job applications and applicant data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "job_id": {"type": "string", "description": "Specific job ID to view applications for"},
                        "status": {"type": "string", "enum": ["all", "pending", "reviewed", "shortlisted", "rejected"]},
                        "limit": {"type": "integer", "description": "Number of applications to return"}
                    }
                }
            },
            {
                "name": "manage_jobs",
                "description": "Manage existing job postings",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["list", "edit", "delete", "activate", "deactivate"]},
                        "job_id": {"type": "string", "description": "Job ID for specific actions"},
                        "status": {"type": "string", "enum": ["Active", "Inactive", "Draft"]}
                    }
                }
            },
            {
                "name": "view_analytics",
                "description": "View recruitment analytics and reports",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "report_type": {"type": "string", "enum": ["applications", "jobs", "performance", "overview"]},
                        "date_range": {"type": "string", "description": "Date range for analytics (e.g., 'last_30_days')"}
                    }
                }
            },
            {
                "name": "create_form",
                "description": "Create a custom form for data collection",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "form_name": {"type": "string", "description": "Name of the form"},
                        "form_description": {"type": "string", "description": "Description of the form"},
                        "fields": {"type": "array", "items": {"type": "object"}, "description": "Form fields configuration"}
                    },
                    "required": ["form_name", "form_description"]
                }
            }
        ]

    def process_message(self, user_message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user message and return appropriate response
        """
        try:
            # Analyze intent using OpenAI
            intent_response = self.analyze_intent(user_message, user_context)
            
            if intent_response.function_call:
                # Execute the action
                action_result = self.execute_action(intent_response.function_call)
                return {
                    "type": "action_response",
                    "content": action_result["message"],
                    "data": action_result.get("data"),
                    "success": action_result.get("success", True)
                }
            else:
                # General conversation response
                return {
                    "type": "conversation",
                    "content": intent_response.content,
                    "success": True
                }
                
        except Exception as e:
            return {
                "type": "error",
                "content": f"I encountered an error: {str(e)}. Please try again or ask for help.",
                "success": False
            }

    def analyze_intent(self, user_message: str, user_context: Dict[str, Any]):
        """
        Use OpenAI to analyze user intent and extract parameters
        """
        system_prompt = f"""You are an AI assistant for a recruitment platform. The user is logged in as {user_context.get('user_role', 'unknown')} with company {user_context.get('company', 'unknown')}.

Available actions:
- post_job: Create new job postings
- view_applications: View job applications
- manage_jobs: Manage existing jobs
- view_analytics: View recruitment analytics
- create_form: Create custom forms

Analyze the user's message and determine what action they want to perform. Extract relevant parameters."""

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            functions=self.functions,
            function_call="auto",
            temperature=0.1
        )
        
        return response.choices[0].message

    def execute_action(self, function_call):
        """
        Execute the determined action
        """
        function_name = function_call.name
        arguments = json.loads(function_call.arguments)
        
        if function_name in self.available_actions:
            return self.available_actions[function_name](arguments)
        else:
            return {
                "success": False,
                "message": f"Action '{function_name}' is not available."
            }

    def post_job_action(self, params: Dict[str, Any]):
        """
        Create a new job posting
        """
        try:
            # Prepare job details
            today = datetime.date.today()
            one_month_later = today + datetime.timedelta(days=30)
            job_details = {
                "job_title": params.get("job_title"),
                "job_description": params.get("job_description"),
                "job_requirements": params.get("job_requirements", ""),
                "job_benefits": params.get("job_benefits", ""),
                "job_type": params.get("job_type", "Full Time"),
                "job_skills":"",
                "work_style": params.get("work_style", "On-Site"),
                "work_experience": params.get("work_experience", "Mid-Level"),
                "industry": params.get("industry", ""),
                "min_salary": float(params.get("min_salary")) if params.get("min_salary") else None,
                "max_salary": float(params.get("max_salary")) if params.get("max_salary") else None,
                "salary_currency": params.get("salary_currency"),
                "salary_time_unit": params.get("salary_time_unit"),
                "address_city": params.get("address_city", ""),
                "address_country": params.get("address_country", ""),
                "address_province": "",
                "address_postal_code": "",
                "target_date": str(one_month_later.strftime("%Y-%m-%d")),
                "opening_date": str(today.strftime("%Y-%m-%d")),
                "job_opening_status": "Active",
                "status": "published"
            }

            print("job_details", job_details)

            # Call API to create job
            result = api_calls.create_job_opening(
                job_detail=job_details,
                access_token=current_user.id
            )
            
            if result:
                return {
                    "success": True,
                    "message": f"✅ Job '{params.get('job_title')}' has been successfully posted! The job is now live and accepting applications.",
                    "data": {"job_id": result.get("id")}
                }
            else:
                return {
                    "success": False,
                    "message": "❌ Failed to create job posting. Please try again or contact support."
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error creating job posting: {str(e)}"
            }

    def view_applications_action(self, params: Dict[str, Any]):
        """
        View job applications
        """
        try:
            # This would integrate with your existing applicant tracking
            job_id = params.get("job_id")
            status = params.get("status", "all")
            
            # Call API to get applications
            # applications = api_calls.get_applications(access_token=current_user.id, job_id=job_id, status=status)
            
            return {
                "success": True,
                "message": f"📋 Here are the applications for job {job_id if job_id else 'all jobs'} (Status: {status})",
                "data": {
                    "applications": [],  # Would contain actual application data
                    "count": 0
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error retrieving applications: {str(e)}"
            }

    def manage_jobs_action(self, params: Dict[str, Any]):
        """
        Manage existing jobs
        """
        action = params.get("action", "list")
        
        if action == "list":
            return {
                "success": True,
                "message": "📋 Here are your current job postings:",
                "data": {"action": "list_jobs"}
            }
        elif action == "edit":
            return {
                "success": True,
                "message": f"✏️ I'll help you edit job {params.get('job_id')}",
                "data": {"action": "edit_job", "job_id": params.get("job_id")}
            }
        else:
            return {
                "success": True,
                "message": f"🔄 Performing {action} action on jobs",
                "data": {"action": action}
            }

    def view_analytics_action(self, params: Dict[str, Any]):
        """
        View recruitment analytics
        """
        report_type = params.get("report_type", "overview")
        date_range = params.get("date_range", "last_30_days")
        
        return {
            "success": True,
            "message": f"📊 Here are your {report_type} analytics for {date_range}:",
            "data": {
                "report_type": report_type,
                "date_range": date_range,
                "analytics": {}  # Would contain actual analytics data
            }
        }

    def create_form_action(self, params: Dict[str, Any]):
        """
        Create a custom form
        """
        form_name = params.get("form_name")
        form_description = params.get("form_description")
        
        return {
            "success": True,
            "message": f"📝 I'll help you create a form called '{form_name}'",
            "data": {
                "form_name": form_name,
                "form_description": form_description,
                "action": "create_form"
            }
        }

    def help_action(self, params: Dict[str, Any] = None):
        """
        Provide help and available commands
        """
        help_text = """🤖 **I can help you with the following tasks:**

**Job Management:**
• "Post a new job for Software Engineer"
• "Create a job posting for Marketing Manager"
• "Show me my current job postings"
• "Edit job posting #123"

**Application Tracking:**
• "Show applications for job #123"
• "View pending applications"
• "Review applications for Software Engineer position"

**Analytics & Reports:**
• "Show me recruitment analytics"
• "View application statistics"
• "Generate performance report"

**Forms & Pages:**
• "Create a custom application form"
• "Build a contact form"

**General:**
• "What can you do?"
• "Help me with job posting"

Just tell me what you'd like to do! 🚀"""

        return {
            "success": True,
            "message": help_text
        }

    def manage_pages_action(self, params: Dict[str, Any]):
        """
        Manage pages (placeholder for future implementation)
        """
        return {
            "success": True,
            "message": "📄 Page management features are coming soon!",
            "data": {"action": "manage_pages"}
        } 