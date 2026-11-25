"""UI-only preview using production templates and entirely synthetic, in-memory data.
Never imports app.py, api_calls, schemas or production configuration.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from datetime import datetime
from flask import render_template, request, redirect, url_for, jsonify, send_from_directory
from flask_login import login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField,SubmitField,validators
from wtforms.validators import DataRequired
from flask_wtf.file import FileField
from offline_app import build_app,ROOT

COMPANY=dict(id=1,name='Hiregen QA Test — Not a Real Employer',company_subdomain='hiregenqa',location='QA Test Location — Profile Retest',company_logo='/__preview/assets/qa-logo.png',cover_image='/__preview/assets/qa-cover.png',description='QA TEST DATA ONLY. Mock employer for authorized Hiregen testing. Not recruiting. Do not apply or contact.')
JOB=dict(id=168,job_title='TEST JOB — Junior QA Engineer (Not Real)',company_name=COMPANY['name'],company_subdomain='hiregenqa',slug='test-job-junior-qa-engineer-not-real',company_logo='',status='published',job_opening_status='Active',job_type='Full Time',industry='Computer Networking',working_style='Remote',address_city='Bengaluru',address_province='Karnataka',address_country='India',created_at='2026-11-19T09:00:00',min_salary=45000,max_salary=60000,salary_currency='$',salary_time_unit='Yearly',salary=None,job_skills=[],applicant_count=1,job_opening_views=27,job_description='<p>TEST VACANCY ONLY. No real hiring, salary or employment offer. Use synthetic applicant data only.</p><ul><li>Write test cases.</li><li>Perform manual web testing.</li><li>Report defects and check regression fixes.</li></ul>',job_requirements='<p>Mock requirements: 0–2 years of experience, basic SQL and clear communication.</p>',job_benefits='<p>Simulated benefits for testing only. No compensation or employment is offered.</p>',saved=False,applied=False)
APPLICANT=dict(application_id=424,applicant_id=818,applicant_name='Hiregen QA Jobseeker Test',applicant_email='hiregen-jobseeker-qa-20261119@example.com',applicant_profile_picture='',application_status='applied',application_date='19 Nov 2026',resume='',job_title=JOB['job_title'],job_url='/jobs/'+JOB['slug'],similarity_scores=dict(overall_score=35,experience_embedding=51,education_embedding=47,skill_embedding=24,leadership_embedding=24,industry_embedding=27))
STAGES=[dict(id=200+i,name=n,description=d,stage_type=t,stage_order=i,created_at='19 Nov 2026',job_status=j) for i,(n,d,t,j) in enumerate([('Applied','Initial application','Applied','applied'),('QA TEST — Screening Retest','Mock screening stage for authorized testing.','Screening','qa-screening'),('Selected','Selected for job','Selected','selected'),('Rejected','Rejected from job','Rejected','rejected')])]

def build_preview():
 app=build_app();app.config.update(SERVER_NAME=None,TESTING=True,WTF_CSRF_ENABLED=False,TEMPLATES_AUTO_RELOAD=True)
 @app.get('/__preview/assets/<name>')
 def fixture_asset(name):return send_from_directory('/Users/amishchawla/Documents/ChatGPT/hiregen/testing-hiregen/employer/fixtures',name)
 user=app.fixture_user;user.role='user';user.username='Hiregen QA Test 20261119';user.company=COMPANY
 user.group={'permissions':['can_manage_jobs','can_track_applicants','can_manage_team']}
 app.api.get_user_all_job_openings=Mock(return_value=dict(jobs=[JOB,{**JOB,'id':169,'job_title':'QA RETEST DRAFT ONLY','slug':'qa-retest-draft','status':'draft','job_opening_status':'Inactive','applicant_count':0,'min_salary':None,'max_salary':None}],metrics=dict(total_jobs=2,active_jobs=1,total_applicants=1,avg_salary='52k')))
 app.api.get_company_job_usage=Mock(return_value=dict(active_jobs=1,active_job_limit=50))
 app.api.get_job_applicants=Mock(return_value=[APPLICANT]);app.api.get_all_applicants=Mock(return_value=[APPLICANT]);app.api.get_applicant_trackers=Mock(return_value=STAGES)
 app.api.get_filtered_applicants_for_employer=Mock(return_value=[APPLICANT]);app.api.get_board_columns=Mock(return_value=STAGES)
 app.api.get_stats=Mock(return_value=dict(total_jobs=2,total_views=27,applicants_count=1,in_progress_jobs=1,mid_stage_applicants_count=0,hiring_rate=0,statuses=[],mid_stage_applicants=[]))
 app.api.read_team_members=Mock(return_value=[])
 app.api.add_team_members=Mock(return_value=True)
 app.api.get_user_preferences=Mock(return_value=dict(email_notifications=True,push_notifications=False,resume_alerts=False,is_public_profile=False))
 app.api.update_user_preferences=Mock(side_effect=lambda **kwargs:kwargs['preferences_update'])
 # Compile the real display routes with mock adapters only; decorators are removed
 # because this fixture has its own explicit mock login and no production auth.
 names={'user_all_post','job_applicants','all_applicants','applicant_tracking','ai_chat','user_dashboard','my_team','employer_settings'}
 env=dict(app=app,render_template=render_template,api_calls=app.api,current_user=__import__('flask_login').current_user,request=request,redirect=redirect,url_for=url_for,flash=__import__('flask').flash,static_dropdowns=SimpleNamespace(job_types=[('Full Time','Full Time')],industries=[('Computer Software','Computer Software')]))
 for n in ast.parse((ROOT/'app.py').read_text()).body:
  if isinstance(n,ast.FunctionDef) and n.name in names:
   route=[d for d in n.decorator_list if isinstance(d,ast.Call) and isinstance(d.func,ast.Attribute) and d.func.attr=='route']
   n.decorator_list=route
   exec(compile(ast.fix_missing_locations(ast.Module(body=[n],type_ignores=[])),'offline_display_route','exec'),env)
 # Real WTForms class extracted in isolation, without importing forms/api_calls.
 form_env=dict(FlaskForm=FlaskForm,StringField=StringField,TextAreaField=TextAreaField,SubmitField=SubmitField,FileField=FileField,validators=validators,DataRequired=DataRequired)
 cls=next(n for n in ast.parse((ROOT/'forms.py').read_text()).body if isinstance(n,ast.ClassDef) and n.name=='EmployerProfileForm')
 exec(compile(ast.Module(body=[cls],type_ignores=[]),'isolated_profile_form','exec'),form_env)
 @app.get('/__preview/login/<role>')
 def preview_login(role):
  if role=='guest':logout_user()
  else:user.role=role;login_user(user)
  return redirect('/user/job-openings' if role=='user' else '/jobs/'+JOB['slug'])
 @app.route('/profile',methods=['GET','POST'])
 def profile():
  form=form_env['EmployerProfileForm'](data=dict(firstname='Hiregen QA',lastname='Test 20261119',username=user.username,email='hiregen-employer-qa-20261119@example.com',phone_number='+12025550147',company_name=COMPANY['name'],company_location=COMPANY['location'],company_website='example.com',company_description=COMPANY['description']))
  if request.method=='POST':return jsonify(saved=True,fields=dict(request.form))
  return render_template('profile.html',form=form,company=COMPANY,is_company_registered=True,current_plan=dict(plan_name='Starter (Free)',status='active',next_billing_date='End of Free Trial'),profile_picture='',job_usage=dict(active_jobs=1,active_job_limit=50))
 @app.get('/__preview/careers')
 def preview_careers():return render_template('company_details.html',company=COMPANY,job_posts=[JOB],rss_feed_url='/offline/rss')
 @app.route('/jobs/'+JOB['slug'],methods=['GET','POST'])
 def preview_job():
  if request.method=='POST':return jsonify(applied=True,fields=dict(request.form))
  return render_template('post.html',company=COMPANY,job_details=JOB,job_id=168,job_slug=JOB['slug'])
 @app.post('/update-application-status')
 def mock_stage_update():
  APPLICANT['application_status']=request.json.get('newStatus','applied')
  return jsonify(success=True,received=request.json)
 @app.post('/application-log/by-application-and-stage')
 def mock_log():return jsonify(log=dict(id=123,event_date='',event_time='',status='scheduled'))
 @app.post('/application-log/update/<int:id>')
 def mock_log_save(id):return jsonify(success=True,received=request.json)
 @app.post('/ai-chat/chat')
 def mock_chat():return jsonify(success=True,session_id='offline',response='This is an offline preview response. No production service was contacted.',message='This is an offline preview response.',type='text')
 @app.post('/ai-chat/session/reset')
 def mock_chat_reset():return jsonify(success=True)
 @app.post('/ai-chat/fetch-user-jobs')
 def mock_jobs():return jsonify(jobs=[JOB],message='Your mock jobs')
 @app.post('/ai-chat/fetch-user-applicants')
 def mock_applicants():return jsonify(applicants=[APPLICANT],message='Your mock applicants')
 @app.post('/ai-chat/post-job')
 def mock_post_job():return jsonify(success=True,message='Mock job saved only in this offline response.')
 return app

if __name__=='__main__':build_preview().run(host='127.0.0.1',port=5067,debug=False)
