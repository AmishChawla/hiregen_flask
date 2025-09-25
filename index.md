# Hiregen.com Overview

Hiregen.com is an advanced recruitment platform designed to streamline the hiring process for employers and jobseekers alike. Leveraging AI-driven technology, Hiregen offers a comprehensive suite of tools that make talent acquisition efficient, collaborative, and data-driven.

## Demo Video

Watch a quick demo of Hiregen.com in action:

[![Hiregen.com Demo Video](documentation/screenshots/HireGen_Demo_Thumbnail.png)](documentation/hiregen_demo_video.mp4)

> Click the image above or [this link](documentation/hiregen_demo_video.mp4) to view the demo video.

Checkout demo at [Hiregen Demo](https://hiregen.com/demo-login)
or
Register at [Employer Registration](https://hiregen.com/register)

## Key Features

### For Employers

- **Application Tracking System (ATS):** Visual Kanban board to track candidates through every stage of the hiring pipeline, from application to onboarding.
- **Job Management:** Easily post, edit, and manage job listings from a centralized dashboard.
- **Candidate Management:** Review, search, and take action on applicants with advanced filtering and bulk actions.
- **Team Collaboration:** Invite colleagues and assign roles to manage hiring collaboratively and securely.
- **Smart Interview Scoring:** Objectively evaluate candidates with AI-powered scoring and comparison tools.
- **Integrated Chat Agent:** Get real-time assistance and best-practice guidance directly within the employer dashboard.
- **Seamless Interview Scheduling:** Schedule interviews, send invites, and coordinate with candidates effortlessly.

### For Jobseekers

- **Personalized Dashboard:** Access a tailored dashboard with AI-based job recommendations that match your skills and experience.
- **Automatic Resume Scanning:** Instantly parse and build your profile from your resume for smarter job matching.
- **Easy Application Process:** Apply to jobs quickly and track your application status in real time.

## Why Choose Hiregen?

- **AI-Powered Matching:** Both employers and jobseekers benefit from intelligent recommendations and automation.
- **Collaboration & Security:** Role-based permissions and team features ensure secure, efficient hiring.
- **User-Friendly Interface:** Intuitive dashboards and workflows for both employers and jobseekers.
- **Comprehensive Support:** Integrated chat agent and detailed documentation to guide users at every step.

With Hiregen.com, organizations can build high-performing teams faster, and jobseekers can discover opportunities that truly fit their aspirations.




## Installation
### 1. Install required libraries
`pip install requirements.txt`

### 2. Configure `secrets.env` and `constants.py`


> [!IMPORTANT]
> Get your google keys from google console.

_secrets.env_
```
OPEN_AI_API_KEY='your api key here'
GOOGLE_CLIENT_ID = 'your api key here'
GOOGLE_CLIENT_SECRET = 'your api key here'
REDIRECT_URI = 'your_redirect_url_here'
```

_constants.py_
```
MY_ROOT_URL = 'your_current_project_url_here'
ROOT_URL = 'your_api_url_here'
BASE_URL = '[your_api_url_here]/api'
```

### 3. Run the project
Run `python app.py` to run this project


## Documentation
[Admin Panel](documentation/admin_panel.md) \
[Employer Panel](documentation/employer_panel.md) \
[Jobseeker Panel](documentation/jobseeker_panel.md)


 
## Demo
Checkout demo at [Hiregen Demo](https://hiregen.com/demo-login)
or
Register at [Employer Registration](https://hiregen.com/register)
