from flask import Blueprint, request, jsonify, session, current_app
from flask_login import login_required, current_user
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from ai_chat_agent import AIChatAgent
import api_calls

# Create Flask blueprint
ai_chat_bp = Blueprint('ai_chat', __name__, url_prefix='/ai-chat')

# Global agent instance
ai_agent = None

def get_ai_agent() -> AIChatAgent:
    """Get or create the global AI chat agent instance"""
    global ai_agent
    if ai_agent is None:
        ai_agent = AIChatAgent()
    return ai_agent

def get_user_id() -> str:
    """Get user ID from current user or session"""
    if current_user and hasattr(current_user, 'id'):
        return str(current_user.id)
    return session.get('user_id', 'anonymous')

def get_session_id() -> str:
    """Get or create session ID for the current conversation"""
    session_id = session.get('ai_chat_session_id')
    if not session_id:
        session_id = f"chat_session_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
        session['ai_chat_session_id'] = session_id
    return session_id

@ai_chat_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    """Main chat endpoint for AI agent interactions"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        message = data.get('message', '').strip()
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get agent and process message
        agent = get_ai_agent()
        user_id = get_user_id()
        session_id = get_session_id()
        
        result = agent.process_message(
            message=message,
            user_id=user_id,
            session_id=session_id
        )
        
        if result.get('success'):
            response_data = {
                'success': True,
                'message': result['message'],
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add job details if available
            if result.get('job_details'):
                response_data['job_details'] = result['job_details']
            
            # Add ready_to_post flag if job is ready
            if result.get('ready_to_post'):
                response_data['ready_to_post'] = True
            
            # Add fetch_user_jobs flag if user wants to see their jobs
            if result.get('fetch_user_jobs'):
                response_data['fetch_user_jobs'] = True
                response_data['maximum_posts'] = result.get('maximum_posts')
            
            # Add fetch_user_applicants flag if user wants to see their applicants
            if result.get('fetch_user_applicants'):
                response_data['fetch_user_applicants'] = True
                response_data['maximum_applicants'] = result.get('maximum_applicants')
            
            return jsonify(response_data)
        else:
            return jsonify({
                'success': False,
                'error': result.get('message', 'Unknown error'),
                'session_id': session_id
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@ai_chat_bp.route('/post-job', methods=['POST'])
@login_required
def post_job():
    """Post the job using the existing API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        session_id = data.get('session_id', get_session_id())
        
        # Get agent and job details
        agent = get_ai_agent()
        job_details = agent.get_job_details_for_posting(session_id)
        
        if not job_details:
            return jsonify({
                'success': False,
                'error': 'No job details found for posting. Please complete the job creation process first.'
            }), 400
        
        # Get access token from current user
        access_token = getattr(current_user, 'id', None)
        if not access_token:
            return jsonify({
                'success': False,
                'error': 'User authentication required'
            }), 401
        
        # Call the existing API to create job
        print("=" * 50)
        print("JOB DETAILS BEING SENT TO API:")
        print("=" * 50)
        for key, value in job_details.items():
            print(f"{key}: {value}")
        print("=" * 50)
        print(f"Access token: {access_token}")
        print("=" * 50)
        
        result = api_calls.create_job_opening(
            job_detail=job_details,
            access_token=access_token
        )
        
        print(f"API result: {result}")
        
        if result:
            # Clear the conversation after successful posting
            agent.clear_conversation(session_id)
            
            return jsonify({
                'success': True,
                'message': f"✅ Job '{job_details.get('job_title')}' has been successfully posted!",
                'job_id': result.get('id') if isinstance(result, dict) else None,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create job posting. The API returned no result. Please check the logs for more details.'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@ai_chat_bp.route('/fetch-user-jobs', methods=['POST'])
@login_required
def fetch_user_jobs():
    """Fetch user's existing job postings"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        maximum_posts = data.get('maximum_posts', 5)  # Default to 5 jobs
        
        # Get access token from current user
        access_token = getattr(current_user, 'id', None)
        if not access_token:
            return jsonify({
                'success': False,
                'error': 'User authentication required'
            }), 401
        
        # Call the existing API to fetch user's jobs
        print("=" * 50)
        print("FETCHING USER'S EXISTING JOBS:")
        print("=" * 50)
        print(f"Access token: {access_token}")
        print(f"Maximum posts: {maximum_posts}")
        print("=" * 50)
        
        result = api_calls.get_user_all_job_openings(
            access_token=access_token,
            maximum_posts=maximum_posts
        )
        
        print(f"API result: {result}")
        print(f"API result type: {type(result)}")
        
        if result:
            # Handle different response formats
            if isinstance(result, list):
                jobs_data = result
                job_count = len(result)
            elif isinstance(result, dict) and 'jobs' in result:
                jobs_data = result['jobs']
                job_count = len(jobs_data) if isinstance(jobs_data, list) else 0
                # Also include metrics if available
                metrics = result.get('metrics', {})
            elif isinstance(result, dict) and 'data' in result:
                jobs_data = result['data']
                job_count = len(jobs_data) if isinstance(jobs_data, list) else 0
            else:
                jobs_data = result
                job_count = 1 if result else 0
            
            print(f"Jobs data: {jobs_data}")
            print(f"Job count: {job_count}")
            
            response_data = {
                'success': True,
                'message': f"Found {job_count} job postings",
                'jobs': jobs_data,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add metrics if available
            if 'metrics' in locals():
                response_data['metrics'] = metrics
            
            return jsonify(response_data)
        else:
            return jsonify({
                'success': True,
                'message': "No job postings found",
                'jobs': [],
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@ai_chat_bp.route('/fetch-user-applicants', methods=['POST'])
@login_required
def fetch_user_applicants():
    """Fetch user's job applicants"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        maximum_applicants = data.get('maximum_applicants', 10)  # Default to 10 applicants
        
        # Get access token from current user
        access_token = getattr(current_user, 'id', None)
        if not access_token:
            return jsonify({
                'success': False,
                'error': 'User authentication required'
            }), 401
        
        # Call the existing API to fetch user's applicants
        print("=" * 50)
        print("FETCHING USER'S APPLICANTS:")
        print("=" * 50)
        print(f"Access token: {access_token}")
        print(f"Maximum applicants: {maximum_applicants}")
        print("=" * 50)
        
        result = api_calls.get_all_applicants(
            access_token=access_token
        )
        
        print(f"API result: {result}")
        print(f"API result type: {type(result)}")
        
        if result:
            # Handle different response formats
            if isinstance(result, list):
                applicants_data = result
                applicant_count = len(result)
            elif isinstance(result, dict) and 'applicants' in result:
                applicants_data = result['applicants']
                applicant_count = len(applicants_data) if isinstance(applicants_data, list) else 0
            elif isinstance(result, dict) and 'data' in result:
                applicants_data = result['data']
                applicant_count = len(applicants_data) if isinstance(applicants_data, list) else 0
            else:
                applicants_data = result
                applicant_count = 1 if result else 0
            
            # Limit to maximum_applicants if specified
            if maximum_applicants and isinstance(applicants_data, list):
                applicants_data = applicants_data[:maximum_applicants]
                applicant_count = len(applicants_data)
            
            print(f"Applicants data: {applicants_data}")
            print(f"Applicant count: {applicant_count}")
            
            return jsonify({
                'success': True,
                'message': f"Found {applicant_count} applicants",
                'applicants': applicants_data,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': True,
                'message': "No applicants found",
                'applicants': [],
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@ai_chat_bp.route('/session/current', methods=['GET'])
@login_required
def get_current_session():
    """Get current session information"""
    try:
        session_id = get_session_id()
        agent = get_ai_agent()
        
        if session_id in agent.conversations:
            conversation = agent.conversations[session_id]
            job_details = conversation.get('job_details')
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'has_job_details': job_details is not None,
                'job_details': job_details.to_dict() if job_details else None,
                'message_count': len(conversation.get('messages', []))
            })
        else:
            return jsonify({
                'success': True,
                'session_id': session_id,
                'has_job_details': False,
                'job_details': None,
                'message_count': 0
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@ai_chat_bp.route('/session/reset', methods=['POST'])
@login_required
def reset_session():
    """Reset the current session"""
    try:
        session_id = get_session_id()
        agent = get_ai_agent()
        
        agent.clear_conversation(session_id)
        
        return jsonify({
            'success': True,
            'message': 'Session reset successfully. You can start a new conversation!',
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@ai_chat_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for AI chat agent service"""
    try:
        agent = get_ai_agent()
        active_sessions = len(agent.conversations)
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'active_sessions': active_sessions,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Error handlers
@ai_chat_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@ai_chat_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# Utility function to register the blueprint with Flask app
def register_ai_chat_blueprint(app):
    """Register the AI chat agent blueprint with the Flask app"""
    app.register_blueprint(ai_chat_bp)
    print("AI Chat Agent blueprint registered successfully")
