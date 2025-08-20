"""
Configuration file for the AI Chatbot Agent
"""

# Job Posting Chatbot Configuration

# OpenAI Configuration
OPENAI_MODEL = "gpt-4"
OPENAI_TEMPERATURE = 0.3
OPENAI_MAX_TOKENS = 1000

# Job Types
JOB_TYPES = [
    "Full Time",
    "Part Time", 
    "Training",
    "Freelance",
    "Seasonal",
    "Contract",
    "Temporary"
]

# Work Styles
WORK_STYLES = [
    "On-Site",
    "Hybrid", 
    "Remote"
]

# Work Experience Levels
WORK_EXPERIENCE_LEVELS = [
    "Fresher/Graduate",
    "Junior",
    "Mid-Level",
    "Senior",
    "Expert"
]

# Salary Currencies (with symbols)
SALARY_CURRENCIES = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "CAD": "C$",
    "AUD": "A$",
    "JPY": "¥",
    "INR": "₹"
}

# Salary Time Units
SALARY_TIME_UNITS = [
    "per hour",
    "per day", 
    "per week",
    "per month",
    "per year"
]

# Conversation States
CONVERSATION_STATES = {
    "INITIAL": "initial",
    "WAITING_FOR_TITLE": "waiting_for_title",
    "WAITING_FOR_ACCEPT_REJECT": "waiting_for_accept_reject", 
    "WAITING_FOR_MODIFICATIONS": "waiting_for_modifications",
    "WAITING_FOR_CONFIRMATION": "waiting_for_confirmation"
}

# Response Templates
RESPONSE_TEMPLATES = {
    "WELCOME": "Hello! I'm your job posting assistant. I can help you create and post job openings with AI-powered suggestions. Just say 'Post a job' or 'Create a job posting' to get started!",
    "ASK_JOB_TITLE": "Please provide the job title for the position you want to post. For example: 'Software Engineer', 'Marketing Manager', 'Customer Service Representative'",
    "MODIFY_PROMPT": "What would you like to modify? You can say things like:\n• 'Change salary to $80,000-$100,000'\n• 'Make it remote work'\n• 'Change job type to part-time'\n• 'Update the requirements'\n• 'Change location to New York'\n\nPlease specify what you want to change:",
    "CLARIFICATION": "I'm not sure what you'd like to do. Please choose:\n1. ✅ Accept these suggestions\n2. ✏️ Modify some details\n3. 🔄 Generate different suggestions\n4. ❌ Cancel job posting",
    "CONFIRMATION_PROMPT": "Please confirm with 'Yes' to post the job or 'No' to make changes."
}

# Error Messages
ERROR_MESSAGES = {
    "GENERAL_ERROR": "I encountered an error. Please try again.",
    "JSON_PARSE_ERROR": "I couldn't parse the AI response. Please try again.",
    "SUGGESTION_ERROR": "I couldn't generate suggestions. Please try again.",
    "MODIFICATION_ERROR": "I couldn't modify the suggestions. Please try again with clearer instructions.",
    "POST_ERROR": "Failed to create job posting. Please try again or contact support."
}

# Quick Actions
QUICK_ACTIONS = [
    "Post a job",
    "What can you do?",
    "Help"
]

# Job Posting Keywords
JOB_POSTING_KEYWORDS = [
    'post a job',
    'create job', 
    'new job',
    'hire',
    'job posting',
    'post job',
    'create a job',
    'job opening',
    'recruit'
]

# User Response Keywords
USER_RESPONSE_KEYWORDS = {
    "ACCEPT": ['accept', 'yes', '1', 'ok', 'good', 'approve'],
    "MODIFY": ['modify', 'change', 'edit', '2', 'update'],
    "REGENERATE": ['regenerate', 'different', 'new', '3', 'generate'],
    "CANCEL": ['cancel', 'stop', 'quit', '4'],
    "CONFIRM": ['yes', 'confirm', 'post', 'ok', 'go ahead', 'proceed'],
    "DECLINE": ['no', 'change', 'modify', 'edit', 'back']
}

# Default Job Values
DEFAULT_JOB_VALUES = {
    "job_type": "Full Time",
    "work_style": "On-Site", 
    "work_experience": "Mid-Level",
    "salary_currency": "$",
    "salary_time_unit": "per year",
    "job_opening_status": "Active",
    "status": "published",
    "job_skills": ""
} 