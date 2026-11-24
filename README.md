# Hiregen.com Overview

Hiregen.com is an advanced recruitment platform designed to streamline the hiring process for employers and jobseekers alike. Leveraging AI-driven technology, Hiregen offers a comprehensive suite of tools that make talent acquisition efficient, collaborative, and data-driven.

## Demo Video

Watch a quick demo of Hiregen.com in action:

[![Hiregen.com Demo Video](documentation/screenshots/demo_video_thumbnail.png)](documentation/hiregen_demo_video.mp4)

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


## Offline regression checks

These checks do not import the production app, load `constants.py`/secrets, or connect to the API/database. The Python suite blocks outgoing socket connections and exercises selected route definitions with synthetic fixtures.

```sh
python3 -m venv /tmp/hiregen-test-env
/tmp/hiregen-test-env/bin/pip install -r requirements-test.txt
PYTHONPATH=.:tests /tmp/hiregen-test-env/bin/pytest -q tests/test_flask_regressions.py
node tests/test_browser_scripts.cjs
```

To preview synthetic pages locally (without production credentials):

```sh
PYTHONPATH=.:tests /tmp/hiregen-test-env/bin/python tests/offline_app.py
```

Open `http://127.0.0.1:5067/` for the homepage, `/__fixtures/login/jobseeker` for the synthetic profile, `/__fixtures/job` for a mock vacancy, and `/__fixtures/blog` for the mobile blog card. Fixture routes exist only in the offline app, not in `app.py`. Do not use the normal production app/configuration for offline checks.

### Stylesheet build

The active layouts use the checked-in `static/css/tailwind.css` instead of the Tailwind browser CDN. After changing template classes:

```sh
npm ci --ignore-scripts
npm run build:css
```

Deploy the generated stylesheet with the Flask templates. Node is needed for rebuilding assets, not for serving Flask.

### AI assistant model

`HIREGEN_CHAT_MODEL` selects the model for the Flask chat agent (default `gpt-4.1`). Configure a model available to the deployment's OpenAI project. The offline tests mock provider calls; they do not verify live model access. Model/API compatibility reference: https://developers.openai.com/api/docs/guides/latest-model?model=gpt-4.1

### Scope of the November 2026 fixes

Security response headers, existing job/blog server errors (including deleted-job handling), test-company moderation, TLS certificates, currency storage/selection, job slug changes on save, and application progress calculations are intentionally unchanged. Draft visibility is filtered in Flask company pages, detail views, and company feeds; the backend API still needs its own publication enforcement. Existing API-generated dated application links are supported through a Flask redirect; backend link generation is unchanged.


### Company-wide free-plan job allowance

The Jobs page reads active-job usage from the backend. The shared free allowance
is 50 published, active jobs per company, including team members' jobs. Closing
or unpublishing a job frees a slot; drafts never consume a slot.

Deploy the FastAPI quota implementation before this Flask update. Include the
new `job_quota_client.py` module in the deployment. A structured backend HTTP 409
quota response re-renders the bound job form with an accessible error message,
so the employer can close an existing job or save the entered job as a draft.
The backend migration `migrations/20261124_free_plan_50_active_jobs.sql` updates
free plan ID 1's stored allowance; it must be applied through the normal database
migration process. No production database update is performed by the Flask app.

Offline validation: `PYTHONPATH=.:tests python -m pytest tests/test_job_quota_client.py tests/test_flask_regressions.py`.
