"""
Configuration file for the AI Chatbot Agent
"""

# OpenAI Configuration
OPENAI_MODEL = "gpt-4"
OPENAI_TEMPERATURE = 0.1
OPENAI_MAX_TOKENS = 1000

# Available Actions and Permissions
AVAILABLE_ACTIONS = {
    "post_job": {
        "name": "Post Job",
        "description": "Create a new job posting",
        "required_permissions": ["can_manage_jobs"],
        "icon": "📝"
    },
    "view_applications": {
        "name": "View Applications", 
        "description": "View job applications",
        "required_permissions": ["can_track_applicants"],
        "icon": "📋"
    },
    "manage_jobs": {
        "name": "Manage Jobs",
        "description": "Manage existing job postings",
        "required_permissions": ["can_manage_jobs"],
        "icon": "⚙️"
    },
    "view_analytics": {
        "name": "View Analytics",
        "description": "View recruitment analytics",
        "required_permissions": ["can_view_analytics"],
        "icon": "📊"
    },
    "create_form": {
        "name": "Create Form",
        "description": "Create custom forms",
        "required_permissions": ["manage_forms"],
        "icon": "📝"
    },
    "manage_pages": {
        "name": "Manage Pages",
        "description": "Manage website pages",
        "required_permissions": ["manage_pages"],
        "icon": "📄"
    }
}

# System Prompts
SYSTEM_PROMPTS = {
    "default": """You are an AI assistant for a recruitment platform. Help users manage their recruitment process efficiently.""",
    
    "job_posting": """You are helping users create job postings. Extract job details from their natural language input and create structured job postings.""",
    
    "applications": """You are helping users manage job applications. Provide insights and help them track applicant progress.""",
    
    "analytics": """You are helping users understand their recruitment analytics. Provide insights and recommendations based on their data."""
}

# Response Templates
RESPONSE_TEMPLATES = {
    "job_created": "✅ Job '{job_title}' has been successfully posted! The job is now live and accepting applications.",
    "job_failed": "❌ Failed to create job posting. Please try again or contact support.",
    "permission_denied": "❌ You don't have permission to perform this action. Please contact your administrator.",
    "action_success": "✅ Action completed successfully!",
    "action_failed": "❌ Action failed. Please try again.",
    "help_general": "🤖 I can help you with job posting, application tracking, analytics, and more. Just tell me what you need!"
}

# Quick Actions for UI
QUICK_ACTIONS = [
    {
        "text": "📝 Post Job",
        "message": "Post a new job",
        "icon": "📝"
    },
    {
        "text": "📋 View Applications", 
        "message": "Show my job applications",
        "icon": "📋"
    },
    {
        "text": "📊 Analytics",
        "message": "Show recruitment analytics",
        "icon": "📊"
    },
    {
        "text": "❓ Help",
        "message": "What can you do?",
        "icon": "❓"
    }
]

# Error Messages
ERROR_MESSAGES = {
    "api_error": "I encountered an error connecting to the system. Please try again.",
    "permission_error": "You don't have permission to perform this action.",
    "validation_error": "Please provide more details for this action.",
    "timeout_error": "The request timed out. Please try again.",
    "general_error": "An unexpected error occurred. Please try again or contact support."
}

# Conversation Settings
CONVERSATION_SETTINGS = {
    "max_history_length": 50,
    "context_window": 10,
    "typing_indicator_delay": 1000,
    "auto_save_interval": 30000  # 30 seconds
}

# UI Configuration
UI_CONFIG = {
    "theme": {
        "primary_color": "#667eea",
        "secondary_color": "#764ba2", 
        "success_color": "#4ade80",
        "error_color": "#ef4444",
        "warning_color": "#f59e0b"
    },
    "animations": {
        "typing_speed": 50,
        "message_fade_in": 300,
        "button_hover_scale": 1.05
    }
} 