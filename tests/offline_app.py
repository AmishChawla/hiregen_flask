"""Offline fixture app: extract selected route definitions without importing app.py.

No credentials, real API adapter, database module or production startup is loaded.
"""
import ast
from datetime import datetime
from functools import wraps
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import xml.etree.ElementTree as ET

from flask import Flask, abort, redirect, render_template, request, url_for, Response, send_file
from flask_login import LoginManager, UserMixin, current_user, login_required
from werkzeug.routing import BuildError
from web_helpers import absolute_website_url, public_hiregen_url, is_public_job, sitemap_entries

ROOT = Path(__file__).resolve().parents[1]

class FixtureUser(UserMixin):
    id = 'synthetic-offline-user'
    user_id = 1
    role = 'jobseeker'
    firstname = 'QA'
    lastname = 'Fixture'
    username = 'QA Fixture'
    email = 'offline@example.com'
    profile_picture = None
    company = {'id': 1, 'name': 'QA Fixture Company'}
    group = {'permissions': ['applicants']}
    employer_permissions = []
    def has_permission(self, allowed):
        return bool(set(allowed) & set(self.group['permissions']))


def build_app():
    app = Flask('hiregen_offline', template_folder=str(ROOT/'templates'), static_folder=str(ROOT/'static'), subdomain_matching=True)
    app.config.update(SECRET_KEY='offline-only', TESTING=True, SERVER_NAME='hiregen.test', SESSION_COOKIE_SECURE=False)
    manager = LoginManager(app)
    manager.login_view = 'login'
    app.jinja_env.auto_reload = True
    from resource_pages import resource_pages
    app.register_blueprint(resource_pages)
    user = FixtureUser()
    manager.user_loader(lambda _id: user)
    api = SimpleNamespace()
    app.api = api
    app.fixture_user = user
    # Only these explicitly mocked functions can be called.
    api.get_sitemap_data = Mock(return_value={'companies': [], 'jobs': [], 'posts': []})
    api.get_company_details_by_subdomain = Mock(return_value={'id': 1, 'name': 'QA Fixture Company'})
    api.get_jobs_by_company_id = Mock(return_value=[])
    api.get_job_by_company_subdomain_slug = Mock(return_value=None)
    api.get_filtered_jobs = Mock(return_value={'jobs': [], 'total_jobs': 0})
    api.get_applicant_trackers = Mock(return_value=[])
    api.get_filtered_applicants_for_employer = Mock(return_value=[])
    namespace = dict(app=app, current_user=current_user, login_required=login_required, wraps=wraps,
        redirect=redirect, url_for=url_for, request=request, abort=abort, render_template=render_template,
        Response=Response, ET=ET, datetime=datetime, send_file=send_file,
        absolute_website_url=absolute_website_url, public_hiregen_url=public_hiregen_url,
        is_public_job=is_public_job, sitemap_entries=sitemap_entries, api_calls=api,
        generate_jobs_rss_feed=lambda jobs, title: '<rss version="2.0"></rss>',
        static_dropdowns=SimpleNamespace(job_types=[], industries=[('Airlines/Aviation','Airlines/Aviation')]))
    tree = ast.parse((ROOT/'app.py').read_text())
    selected = {'requires_any_permission','presentation_metadata','index','resources_index','features_index',
        'legacy_about','legacy_contact','legacy_privacy','legacy_signup','legacy_cost_per_hire',
        'legacy_recruiting_roi','legacy_turnover_cost','legacy_application_job_link','sitemap','sitemap_by_key',
        'industry_jobs_rss_feed','jobs_search','employer_applicants_filter','employer_applicants_search',
        'company_details_by_company_subdomain','get_post_by_company_subdomain_and_slug'}
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in selected]
    # Define the permission wrapper before any decorated view.
    nodes.sort(key=lambda n: n.name != 'requires_any_permission')
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(ROOT/'app.py'), 'exec'), namespace)
    app.jinja_env.filters['absolute_website_url'] = absolute_website_url
    # Fixture-only stand-ins for navigation. No external services.
    routes = {
        'login':'/employer/login','jobseeker_login':'/jobseeker/login',
        'about_us':'/aboutus','homepage_contactus_submission':'/contactus',
        'privacy_policy':'/privacy-policy','terms_of_service':'/terms-of-service',
        'faqs':'/faqs','all_companies':'/companies','all_cms_post':'/blog',
        'resources_cost_per_hire':'/resources/cost-per-hire', 'resources_time_to_hire':'/resources/time-to-hire',
        'resources_recruitment_roi':'/resources/recruitment-roi','resources_attrition_cost':'/resources/attrition-cost',
        'resources_job_board_effectiveness':'/resources/job-board-effectiveness',
        'academy.index':'/academy/','rss_feeds_index':'/rss-feeds',
        'get_post_by_company_subdomain_and_slug':'/jobs/<job_slug>'}
    for endpoint, route in routes.items():
        if endpoint in app.view_functions:
            continue
        app.add_url_rule(route, endpoint, lambda **_: 'Offline fixture')
    real_url_for = url_for
    def fixture_url_for(endpoint, **values):
        try: return real_url_for(endpoint, **values)
        except BuildError: return '/offline/' + endpoint
    app.jinja_env.globals['url_for'] = fixture_url_for
    @app.get('/__fixtures/login/<role>')
    def fixture_login(role):
        from flask_login import login_user
        user.role = role
        user.group = {'permissions': ['applicants'] if role == 'jobseeker' else ['can_manage_jobs','can_track_applicants']}
        login_user(user)
        return redirect('/__fixtures/profile')
    @app.get('/__fixtures/profile')
    def profile_fixture():
        profile = dict(profile_summary='QA synthetic profile for local testing only.', skills='React, SQL',
            leadership_keywords='', industry_keywords='', address_city='Bengaluru',address_province='Karnataka',
            address_county='India',languages=['English'],linkedin='',github='',instagram='',portfolio_website='',
            experiences=[dict(position='QA Engineer',company_name='QA Company',start_date=None,end_date=None,is_ongoing=False,responsibilities='Synthetic experience')],
            education=[dict(degree='BSc',field_of_study='Computer Science',institution_name='QA Institute',start_date=None,end_date=None,is_ongoing=False)],
            internships=[],projects=[],accomplishments=[])
        # Forms are never submitted in these fixtures.
        class Field:
            def __call__(self, *a, **kw):return ''
            label='Offline field'
            errors=[]
        class Form:
            def __getattr__(self, name):return Field()
        forms={name:Form() for name in ['about_form','education_form','experience_form','internship_form','project_form','name_form','email_form','phone_form','accomplishment_form','profile_picture_form']}
        return render_template('jobseeker/jobseeker_manage_profile.html',profile_info=profile,resumes=[],root_url='',**forms)
    @app.get('/__fixtures/job')
    def job_fixture():
        class ApplyForm:
            def hidden_tag(self):return ''
        job = dict(id=1,job_title='TEST JOB — Local QA Engineer',company_name='QA Fixture Company',company_subdomain='qa',slug='local-qa',
            company_logo='',address_city='Bengaluru',address_province='Karnataka',address_country='India',
            min_salary=45000,max_salary=60000,salary_currency='$',salary_time_unit='Yearly',salary=None,
            created_at='2026-11-20',job_type='Full Time',job_description='Synthetic vacancy for local testing only.',
            job_requirements='Use mock data.',job_benefits='No real employment.',applied=False,saved=False)
        return render_template('post.html', job_details=job, job_id=1,job_slug='local-qa', company={'name':'QA Fixture Company'},form=ApplyForm())
    @app.get('/__fixtures/search')
    def search_fixture():
        return render_template('jobseeker/jobs_search_2.html', jobs=[],total_job_count=0,countries=[],industries=[],job_types=[('Full Time','Full Time')],prefilled_data=dict(keyword='QA',state='Karnataka',industry='Software',job_type='Full Time',date_filter='week',country='',company_subdomain=''))
    @app.get('/__fixtures/blog')
    def blog_fixture():
        post=dict(title='A very long recruitment article title to verify mobile wrapping',short_description='Synthetic blog card used for offline layout testing.',content='',featured_image='',slug='fixture',created_at='20 Nov 2026')
        return render_template('all_posts.html',result=[post],categories=[])
    return app

if __name__ == '__main__':
    app = build_app()
    app.config['SERVER_NAME'] = None
    app.config['TESTING'] = False
    app.run(host='127.0.0.1',port=5067,debug=False)
