import openai
import json
import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class JobDetails:
    """Data class for job details"""
    job_title: str
    job_description: str
    job_requirements: str
    job_benefits: str
    job_type: str
    working_style: str
    work_experience: str
    industry: str
    min_salary: float
    max_salary: float
    salary_currency: str
    salary_time_unit: str
    address_city: str
    address_country: str
    address_province: str
    address_postal_code: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for API"""
        today = datetime.date.today()
        target_date = today + datetime.timedelta(days=30)
        
        return {
            "job_title": self.job_title,
            "job_description": self.job_description,
            "job_requirements": self.job_requirements,
            "job_benefits": self.job_benefits,
            "job_type": self.job_type,
            "job_skills": "",
            "working_style": self.working_style,  # Changed from working_style to working_style
            "work_experience": self.work_experience,
            "industry": self.industry,
            "min_salary": self.min_salary,
            "max_salary": self.max_salary,
            "salary_currency": self.salary_currency,
            "salary_time_unit": self.salary_time_unit,
            "address_city": self.address_city,
            "address_country": self.address_country,
            "address_province": self.address_province,
            "address_postal_code": self.address_postal_code,
            "target_date": str(target_date),
            "opening_date": str(today),
            "job_opening_status": "Active",
            "status": "published"
        }

class AIChatAgent:
    """AI Chat Agent that uses OpenAI for natural conversation and intent recognition"""
    
    def __init__(self):
        self.conversations: Dict[str, Dict[str, Any]] = {}
        
        # Available options for job creation
        self.job_types = [
            "Full Time", "Part Time", "Training", "Freelance", 
            "Seasonal", "Contract", "Temporary"
        ]
        
        self.work_styles = ["On-Site", "Hybrid", "Remote"]
        
        self.work_experience_levels = [
            "Fresher/Graduate", "Junior", "Mid-Level", "Senior", "Expert"
        ]
        
        self.industries = [
            "Accounting", "Airlines/Aviation", "Alternative Dispute Resolution",
            "Alternative Medicine", "Animation", "Apparel & Fashion",
            "Architecture & Planning", "Arts & Crafts", "Automotive",
            "Aviation & Aerospace", "Banking", "Biotechnology",
            "Broadcast Media", "Building Materials", "Business Supplies & Equipment",
            "Capital Markets", "Chemicals", "Civic & Social Organization",
            "Civil Engineering", "Commercial Real Estate", "Computer & Network Security",
            "Computer Games", "Computer Hardware", "Computer Networking",
            "Computer Software", "Construction", "Consumer Electronics",
            "Consumer Goods", "Consumer Services", "Cosmetics", "Dairy",
            "Defense & Space", "Design", "Education Management", "E-learning",
            "Electrical & Electronic Manufacturing", "Entertainment",
            "Environmental Services", "Events Services", "Executive Office",
            "Facilities Services", "Farming", "Financial Services", "Fine Art",
            "Fishery", "Food & Beverages", "Food Production", "Fundraising",
            "Furniture", "Gambling & Casinos", "Glass, Ceramics & Concrete",
            "Government Administration", "Government Relations", "Graphic Design",
            "Health, Wellness & Fitness", "Higher Education", "Hospital & Health Care",
            "Hospitality", "Human Resources", "Import & Export",
            "Individual & Family Services", "Industrial Automation",
            "Information Services", "Information Technology & Services",
            "Insurance", "International Affairs", "International Trade & Development",
            "Internet", "Investment Banking/Venture", "Investment Management",
            "Judiciary", "Law Enforcement", "Law Practice", "Legal Services",
            "Legislative Office", "Leisure & Travel", "Libraries",
            "Logistics & Supply Chain", "Luxury Goods & Jewelry", "Machinery",
            "Management Consulting", "Maritime", "Marketing & Advertising",
            "Market Research", "Mechanical or Industrial Engineering",
            "Media Production", "Medical Device", "Medical Practice",
            "Mental Health Care", "Military", "Mining & Metals",
            "Motion Pictures & Film", "Museums & Institutions", "Music",
            "Nanotechnology", "Newspapers", "Nonprofit Organization Management",
            "Oil & Energy", "Online Publishing", "Outsourcing/Offshoring",
            "Package/Freight Delivery", "Packaging & Containers",
            "Paper & Forest Products", "Performing Arts", "Pharmaceuticals",
            "Philanthropy", "Photography", "Plastics", "Political Organization",
            "Primary/Secondary", "Printing", "Professional Training",
            "Program Development", "Public Policy", "Public Relations",
            "Public Safety", "Publishing", "Railroad Manufacture", "Ranching",
            "Real Estate", "Recreational", "Facilities & Services",
            "Religious Institutions", "Renewables & Environment", "Research",
            "Restaurants", "Retail", "Security & Investigations",
            "Semiconductors", "Shipbuilding", "Sporting Goods", "Sports",
            "Staffing & Recruiting", "Supermarkets", "Telecommunications",
            "Textiles", "Think Tanks", "Tobacco", "Translation & Localization",
            "Transportation/Trucking/Railroad", "Utilities", "Venture Capital",
            "Veterinary", "Warehousing", "Wholesale", "Wine & Spirits",
            "Wireless", "Writing & Editing"
        ]
        
        self.salary_currencies = ["$", "€", "£", "C$", "A$", "¥", "₹"]
        self.salary_time_units = ["Yearly", "Hourly", "Daily", "Weekly", "Monthly"]
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the AI agent"""
        return f"""You are a helpful AI assistant that can help users create and post job openings, and view their existing jobs. You have access to job posting functionality and can engage in natural conversations.

Your capabilities:
1. Help users create job postings through natural conversation
2. Generate realistic job details using AI
3. Allow users to modify job details naturally
4. Post jobs when the user is ready
5. Show users their existing job postings when requested
6. Show users their job applicants when requested

Available job types: {', '.join(self.job_types)}
Available work styles: {', '.join(self.work_styles)}
Available experience levels: {', '.join(self.work_experience_levels)}
Available industries: {', '.join(self.industries[:10])}... (and many more)
Available salary currencies: {', '.join(self.salary_currencies)}
Available salary time units: {', '.join(self.salary_time_units)}

Conversation guidelines:
- Be friendly, helpful, and professional
- Ask clarifying questions when needed
- When generating job details, tell the user you're creating a comprehensive job posting with all necessary fields
- Generate realistic job details based on the role automatically
- Allow natural modifications to any job aspect
- When the user confirms they want to post, tell them you're preparing the job for posting (don't say it's already posted)
- When users ask to see their jobs, fetch and display their existing job postings
- When users ask to see their applicants, fetch and display their job applicants
- Maintain context throughout the conversation

When a user wants to post a job, help them through the process naturally without rigid steps.
When a user asks to see their jobs, fetch their existing job postings and display them in a user-friendly format.
When a user asks to see their applicants, fetch their job applicants and display them in a user-friendly format."""
    
    def get_functions(self) -> List[Dict[str, Any]]:
        """Define the functions that the AI can call"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "generate_job_details",
                    "description": "Generate complete job details for a given job title",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "job_title": {
                                "type": "string",
                                "description": "The job title for the position"
                            },
                            "job_description": {
                                "type": "string",
                                "description": "Detailed job description (2-3 paragraphs)"
                            },
                            "job_requirements": {
                                "type": "string",
                                "description": "Key requirements and qualifications"
                            },
                            "job_benefits": {
                                "type": "string",
                                "description": "Attractive benefits package"
                            },
                            "job_type": {
                                "type": "string",
                                "enum": self.job_types,
                                "description": "Type of employment"
                            },
                            "working_style": {
                                "type": "string",
                                "enum": self.work_styles,
                                "description": "Work location style"
                            },
                            "work_experience": {
                                "type": "string",
                                "enum": self.work_experience_levels,
                                "description": "Required experience level"
                            },
                            "industry": {
                                "type": "string",
                                "enum": self.industries,
                                "description": "Industry sector"
                            },
                            "min_salary": {
                                "type": "number",
                                "description": "Minimum salary (numeric value)"
                            },
                            "max_salary": {
                                "type": "number",
                                "description": "Maximum salary (numeric value)"
                            },
                            "salary_currency": {
                                "type": "string",
                                "enum": self.salary_currencies,
                                "description": "Salary currency symbol"
                            },
                            "salary_time_unit": {
                                "type": "string",
                                "enum": self.salary_time_units,
                                "description": "Salary time unit"
                            },
                            "address_city": {
                                "type": "string",
                                "description": "City for the job location"
                            },
                            "address_country": {
                                "type": "string",
                                "description": "Country for the job location"
                            },
                            "address_province": {
                                "type": "string",
                                "description": "Province/State for the job location"
                            },
                            "address_postal_code": {
                                "type": "string",
                                "description": "Postal code for the job location"
                            }
                        },
                        "required": ["job_title", "job_description"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "post_job",
                    "description": "Post a job using the provided job details. Only call this when the user has confirmed they want to post the job.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "job_details": {
                                "type": "object",
                                "description": "Complete job details object"
                            }
                        },
                        "required": ["job_details"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_user_jobs",
                    "description": "Fetch and display the user's existing job postings. Call this when the user asks to see their jobs, view their postings, or check what jobs they have posted.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "maximum_posts": {
                                "type": "integer",
                                "description": "Maximum number of jobs to fetch (defaults to 5 jobs)"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_user_applicants",
                    "description": "Fetch and display the user's job applicants. Call this when the user asks to see their applicants, view candidates, check applications, or see who applied to their jobs.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "maximum_applicants": {
                                "type": "integer",
                                "description": "Maximum number of applicants to fetch (defaults to 10 applicants)"
                            }
                        },
                        "required": []
                    }
                }
            }
        ]
    
    def process_message(self, message: str, user_id: str, session_id: str) -> Dict[str, Any]:
        """Process a user message using OpenAI with function calling"""
        try:
            # Get or create conversation
            if session_id not in self.conversations:
                self.conversations[session_id] = {
                    "user_id": user_id,
                    "messages": [
                        {"role": "system", "content": self.get_system_prompt()}
                    ],
                    "job_details": None
                }
            
            conversation = self.conversations[session_id]
            
            # Add user message
            conversation["messages"].append({"role": "user", "content": message})
            
            # Call OpenAI with function calling
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=conversation["messages"],
                tools=self.get_functions(),
                tool_choice="auto",
                temperature=0.7,
                max_tokens=1000
            )
            
            response_message = response.choices[0].message
            
            # Handle tool calls
            if response_message.tool_calls:
                tool_call = response_message.tool_calls[0]
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name == "generate_job_details":
                    return self._handle_generate_job_details(function_args, conversation, response_message)
                elif function_name == "post_job":
                    return self._handle_post_job(function_args, conversation, response_message)
                elif function_name == "get_user_jobs":
                    return self._handle_get_user_jobs(function_args, conversation, response_message)
                elif function_name == "get_user_applicants":
                    return self._handle_get_user_applicants(function_args, conversation, response_message)
            
            # Add assistant response to conversation
            conversation["messages"].append(response_message)
            
            return {
                "success": True,
                "message": response_message.content,
                "session_id": session_id,
                "job_details": conversation.get("job_details")
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "success": False,
                "message": f"I encountered an error: {str(e)}. Please try again.",
                "session_id": session_id
            }
    
    def _handle_generate_job_details(self, args: Dict[str, Any], conversation: Dict[str, Any], response_message) -> Dict[str, Any]:
        """Handle job details generation"""
        try:
            # Create JobDetails object with default values for missing fields
            job_details = JobDetails(
                job_title=args.get("job_title", "Unknown Position"),
                job_description=args.get("job_description", "Job description will be provided."),
                job_requirements=args.get("job_requirements", "Requirements will be specified."),
                job_benefits=args.get("job_benefits", "Benefits package available."),
                job_type=args.get("job_type", "Full Time"),
                working_style=args.get("working_style", "On-Site"),
                work_experience=args.get("work_experience", "Mid-Level"),
                industry=args.get("industry", "Information Technology & Services"),
                min_salary=args.get("min_salary", 50000),
                max_salary=args.get("max_salary", 80000),
                salary_currency=args.get("salary_currency", "$"),
                salary_time_unit=args.get("salary_time_unit", "Yearly"),
                address_city=args.get("address_city", "Remote"),
                address_country=args.get("address_country", "United States"),
                address_province=args.get("address_province", ""),
                address_postal_code=args.get("address_postal_code", "")
            )
            
            # Store in conversation
            conversation["job_details"] = job_details
            
            # Add tool call to conversation
            conversation["messages"].append(response_message)
            
            # Add tool response message
            tool_call = response_message.tool_calls[0]
            tool_response = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(job_details.to_dict())
            }
            conversation["messages"].append(tool_response)
            
            # Get the next response from OpenAI
            next_response = openai.chat.completions.create(
                model="gpt-4",
                messages=conversation["messages"],
                temperature=0.7,
                max_tokens=1000
            )
            
            next_message = next_response.choices[0].message
            conversation["messages"].append(next_message)
            
            return {
                "success": True,
                "message": next_message.content,
                "session_id": conversation.get("session_id"),
                "job_details": job_details.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error handling job details generation: {e}")
            return {
                "success": False,
                "message": f"Error generating job details: {str(e)}",
                "session_id": conversation.get("session_id")
            }
    
    def _handle_post_job(self, args: Dict[str, Any], conversation: Dict[str, Any], response_message) -> Dict[str, Any]:
        """Handle job posting"""
        try:
            # Add tool call to conversation
            conversation["messages"].append(response_message)
            
            # Add tool response message
            tool_call = response_message.tool_calls[0]
            tool_response = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": "Job details prepared for posting"
            }
            conversation["messages"].append(tool_response)
            
            # Get the next response from OpenAI
            next_response = openai.chat.completions.create(
                model="gpt-4",
                messages=conversation["messages"],
                temperature=0.7,
                max_tokens=1000
            )
            
            next_message = next_response.choices[0].message
            conversation["messages"].append(next_message)
            
            # Return job details for posting
            job_details = conversation.get("job_details")
            
            return {
                "success": True,
                "message": "Perfect! I've prepared your job posting. Click the 'Post Job' button below to publish it to your job board.",
                "session_id": conversation.get("session_id"),
                "job_details": job_details.to_dict() if job_details else None,
                "ready_to_post": True
            }
            
        except Exception as e:
            logger.error(f"Error handling job posting: {e}")
            return {
                "success": False,
                "message": f"Error preparing job for posting: {str(e)}",
                "session_id": conversation.get("session_id")
            }
    
    def _handle_get_user_jobs(self, args: Dict[str, Any], conversation: Dict[str, Any], response_message) -> Dict[str, Any]:
        """Handle fetching user's existing jobs"""
        try:
            # Add tool call to conversation
            conversation["messages"].append(response_message)
            
            # Add tool response message
            tool_call = response_message.tool_calls[0]
            tool_response = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": "Fetching user's existing job postings..."
            }
            conversation["messages"].append(tool_response)
            
            # Return immediately without generating additional AI response
            return {
                "success": True,
                "message": "",  # Empty message - no AI response needed
                "session_id": conversation.get("session_id"),
                "fetch_user_jobs": True,
                "maximum_posts": args.get("maximum_posts", 5)  # Default to 5 jobs
            }
            
        except Exception as e:
            logger.error(f"Error handling get_user_jobs: {e}")
            return {
                "success": False,
                "message": f"Error fetching user's jobs: {str(e)}",
                "session_id": conversation.get("session_id")
            }
    
    def _handle_get_user_applicants(self, args: Dict[str, Any], conversation: Dict[str, Any], response_message) -> Dict[str, Any]:
        """Handle fetching user's job applicants"""
        try:
            # Add tool call to conversation
            conversation["messages"].append(response_message)
            
            # Add tool response message
            tool_call = response_message.tool_calls[0]
            tool_response = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": "Fetching user's job applicants..."
            }
            conversation["messages"].append(tool_response)
            
            # Return immediately without generating additional AI response
            return {
                "success": True,
                "message": "",  # Empty message - no AI response needed
                "session_id": conversation.get("session_id"),
                "fetch_user_applicants": True,
                "maximum_applicants": args.get("maximum_applicants", 10)  # Default to 10 applicants
            }
            
        except Exception as e:
            logger.error(f"Error handling get_user_applicants: {e}")
            return {
                "success": False,
                "message": f"Error fetching user's applicants: {str(e)}",
                "session_id": conversation.get("session_id")
            }
    
    def get_job_details_for_posting(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get job details ready for API posting"""
        if session_id in self.conversations:
            conversation = self.conversations[session_id]
            job_details = conversation.get("job_details")
            if job_details:
                return job_details.to_dict()
        return None
    
    def clear_conversation(self, session_id: str):
        """Clear a conversation session"""
        if session_id in self.conversations:
            del self.conversations[session_id]
