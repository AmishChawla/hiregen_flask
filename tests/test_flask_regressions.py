import ast
from pathlib import Path
import socket
from types import SimpleNamespace
from unittest.mock import Mock
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
from flask import request
import pytest
from web_helpers import absolute_website_url, is_public_job, public_hiregen_url
from offline_app import build_app, ROOT

@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def blocked(*a,**kw):raise AssertionError('Network access forbidden in offline tests')
    monkeypatch.setattr(socket.socket,'connect',blocked)
    monkeypatch.setattr(socket,'create_connection',blocked)

@pytest.fixture
def app(): return build_app()

@pytest.mark.parametrize('value,expected',[('example.com','https://example.com'),('//example.com/a','https://example.com/a'),('https://example.com/a?x=1&y=2','https://example.com/a?x=1&y=2'),('javascript:alert(1)',None),('data:text/html,x',None),('https://u:p@example.com',None),('',None),('https://example.com:bad',None)])
def test_website_urls(value,expected):assert absolute_website_url(value)==expected

@pytest.mark.parametrize('value',["https://https://invozone.com.hiregen.com/",'https://other.example/','https://bad_.hiregen.com/'])
def test_sitemap_rejects_malformed_urls(value):assert public_hiregen_url(value) is None

def test_sitemap_escapes_and_deduplicates(app):
    app.api.get_sitemap_data.return_value={'companies':[{'url':'https://qa.hiregen.com/?a=1&b=2'},{'url':'https://https://broken/'}],'jobs':[],'posts':[]}
    response=app.test_client().get('/sitemap.xml')
    assert response.status_code==200
    root=ET.fromstring(response.data)
    urls=[n.text for n in root.findall('{*}url/{*}loc')]
    assert 'https://qa.hiregen.com/?a=1&b=2' in urls
    assert 'https://hiregen.test/aboutus' not in urls
    assert len(urls)==len(set(urls))
    # Production host is the only host emitted by real app configuration.
    assert not any('broken' in u for u in urls)

def test_keyed_sitemap_escapes(app):
    app.api.get_sitemap_data.return_value={'jobs':[{'url':'https://qa.hiregen.com/jobs/a?x=1&y=2'}]}
    response=app.test_client().get('/sitemap/jobs/sitemap.xml')
    assert response.status_code==200
    assert ET.fromstring(response.data).find('{*}url/{*}loc').text.endswith('?x=1&y=2')

def test_unknown_sitemap_key(app):assert app.test_client().get('/sitemap/unknown/sitemap.xml').status_code==404

def test_signed_out_permission_guard_redirects_before_api(app):
    response=app.test_client().get('/employer/applicants/filter')
    assert response.status_code==302
    assert '/employer/login' in response.location
    app.api.get_applicant_trackers.assert_not_called()

def test_jobseeker_guard_redirects_to_jobseeker_login(app):
    guard=app.view_functions['employer_applicants_filter'].__wrapped__
    with app.test_request_context('/jobseeker/profile'):
        response=guard()
        assert '/jobseeker/login' in response.location

def test_limited_member_is_denied_before_search(app):
    c=app.test_client()
    c.get('/__fixtures/login/employer')
    app.fixture_user.group={'permissions':['can_manage_jobs']}
    response=c.get('/employer/applicants/search?name=QA')
    assert response.status_code==403
    app.api.get_applicant_trackers.assert_not_called()
    app.api.get_filtered_applicants_for_employer.assert_not_called()

def test_missing_search_results_are_an_empty_state(app):
    c=app.test_client();c.get('/__fixtures/login/employer')
    app.api.get_filtered_applicants_for_employer.return_value=None
    response=c.get('/employer/applicants/search?name=QA')
    assert response.status_code==200
    assert b'No applicants match your search' in response.data

def test_dated_job_link_redirects_without_api(app):
    response=app.test_client().get('/jobs/2026-11-19/qa-test',base_url='http://qa.hiregen.test')
    assert response.status_code==301
    assert response.location.endswith('/jobs/qa-test?company_subdomain=qa') or response.location.endswith('/jobs/qa-test')

def test_invalid_legacy_date(app):
    response=app.test_client().get('/jobs/2026-19-31/qa',base_url='http://qa.hiregen.test')
    assert response.status_code==404

def test_public_listing_filters_drafts_and_inactive_jobs():
    jobs=[dict(status='draft',job_opening_status='Active'),dict(status='published',job_opening_status='Inactive'),dict(status='published',job_opening_status='Active')]
    assert list(filter(is_public_job,jobs))==[jobs[2]]

def test_rss_slash_industry_reaches_api(app):
    response=app.test_client().get('/rss/industry/airlines/aviation/jobs.xml')
    # Feed content is stubbed; test slash routing and exact API enum.
    app.api.get_filtered_jobs.assert_called_once_with(industry='Airlines/Aviation',limit=50)
    assert response.status_code==200

def test_profile_does_not_invent_qualifications(app):
    c=app.test_client();c.get('/__fixtures/login/jobseeker');r=c.get('/__fixtures/profile')
    assert r.status_code==200
    text=BeautifulSoup(r.data,'html.parser').get_text(' ',strip=True)
    assert '3.8/4.0' not in text and '2015 - 2019' not in text
    assert 'End date not specified' in text
    assert 'Present' not in text

def test_filters_preserved_in_main_search_form(app):
    c=app.test_client();c.get('/__fixtures/login/jobseeker');r=c.get('/__fixtures/search')
    soup=BeautifulSoup(r.data,'html.parser')
    form=soup.select_one('#keyword').find_parent('form')
    assert form.find('input',{'name':'job_type'})['value']=='Full Time'
    assert form.find('input',{'name':'industry'})['value']=='Software'
    assert form.find('input',{'name':'date_filter'})['value']=='week'

def test_job_confirmation_identifies_submission(app):
    c=app.test_client();c.get('/__fixtures/login/jobseeker');r=c.get('/__fixtures/job')
    assert r.status_code==200
    soup=BeautifulSoup(r.data,'html.parser');modal=soup.select_one('#applyModal')
    assert 'using your current Hiregen profile' in modal.get_text()
    assert 'QA Fixture Company' in modal.get_text()

def test_editor_form_and_sync_target_match():
    source=(ROOT/'templates/edit_post_form.html').read_text()
    soup=BeautifulSoup(source,'html.parser')
    assert soup.select_one('#editjobForm') is not None
    assert 'document.querySelector("#editjobForm")' in source

@pytest.mark.parametrize('path,target',[('/about','/aboutus'),('/contact','/contactus'),('/privacy','/privacy-policy'),('/signup','/register'),('/cost-per-hire-calculator','/resources/cost-per-hire')])
def test_public_aliases(app,path,target):
    r=app.test_client().get(path);assert r.status_code==301 and r.location.endswith(target)

def test_faq_accessible_controls(app):
    r=app.test_client().get('/');assert r.status_code==200
    soup=BeautifulSoup(r.data,'html.parser')
    for i in range(1,10):
        button=soup.select_one(f'#faqButton{i}')
        assert button.name=='button' and button['aria-controls']==f'para{i}'
        assert button['aria-expanded']=='false'

def test_no_browser_tailwind_cdn():
    active = ['index.html','base.html','common_base.html','company_base.html','jobseeker/jobseeker_base.html','admin_base.html','post.html']
    assert all('cdn.tailwindcss.com' not in (ROOT/'templates'/name).read_text() for name in active)

def test_python_and_jinja_parse(app):
    for name in ['app.py','web_helpers.py','ai_chat_agent.py','academy_routes.py']:
        ast.parse((ROOT/name).read_text())
    for name in app.jinja_env.list_templates():
        if name.endswith(('.html','.xml')):
            app.jinja_env.parse(app.jinja_env.loader.get_source(app.jinja_env,name)[0])

def test_ai_model_and_friendly_error(monkeypatch):
    import importlib.util
    import sys
    fake_create=Mock()
    fake_create.return_value=SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='Mock response',tool_calls=[]))])
    monkeypatch.setitem(sys.modules,'openai',SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=fake_create))))
    spec=importlib.util.spec_from_file_location('offline_ai_agent',ROOT/'ai_chat_agent.py')
    mod=importlib.util.module_from_spec(spec);monkeypatch.setitem(sys.modules,spec.name,mod);spec.loader.exec_module(mod)
    monkeypatch.setenv('HIREGEN_CHAT_MODEL','configured-test-model')
    agent=mod.AIChatAgent();result=agent.process_message('Show me my jobs','mock-user','mock-session')
    assert result['success'] is True
    assert fake_create.call_args.kwargs['model']=='configured-test-model'
    fake_create.side_effect=RuntimeError('provider-secret-raw-payload')
    result=agent.process_message('Show me my jobs','mock-user','mock-session-2')
    assert result['success'] is False
    assert 'provider-secret' not in result['message']
    assert 'try again' in result['message'].lower()

def test_no_excluded_backend_changes():
    # These exact excluded values/behaviors must not be rewritten by this Flask patch.
    assert "currency['symbol']" in (ROOT/'forms.py').read_text()
    source=(ROOT/'templates/jobseeker/jobseeker_complete_application_details.html').read_text()
    assert 'application_timeline.progress_percentage' in source

@pytest.mark.parametrize('path',['/interview-cost-calculator','/job-posting-cost-calculator','/offer-acceptance-rate','/quality-of-hire-calculator','/recruitment-agency-fee-calculator','/recruitment-budget-calculator','/sourcing-channel-roi','/time-to-fill-calculator','/resources/pipeline-conversion-calculator','/resources/cost-of-bad-hire-calculator','/headcount-planning-template'])
def test_broken_resource_destinations_render_offline(app,path):
    response=app.test_client().get(path,follow_redirects=True)
    assert response.status_code==200
    soup=BeautifulSoup(response.data,'html.parser')
    assert len(soup.find_all('h1'))==1

def test_chart_initialization_handles_absent_canvases_and_empty_data(app,tmp_path):
    import re
    import subprocess
    template=(ROOT/'templates/dashboard.html').read_text()
    script=next(s for s in re.findall(r'<script>([\s\S]*?)</script>',template) if 'jobsCanvas' in s)
    rendered=app.jinja_env.from_string(script).render(total_jobs=0,in_progress_jobs=0,applicants_count=0,statuses=[])
    runner=tmp_path/'charts.cjs'
    runner.write_text("const vm=require('node:vm'); const assert=require('node:assert/strict'); const script="+__import__('json').dumps(rendered)+";\n"+'''
    vm.runInNewContext(script,{document:{getElementById:()=>null}});
    const configs=[];
    vm.runInNewContext(script,{document:{getElementById:()=>({getContext:()=>({})})},Chart:function(ctx,config){configs.push(config)}});
    assert.equal(configs.length,2);
    for (const config of configs) assert(Number.isFinite(config.options.scales.y.ticks.max));
    ''')
    subprocess.run(['node',str(runner)],check=True,capture_output=True,text=True)

def test_guest_cannot_open_draft_detail(app):
    app.api.get_job_by_company_subdomain_slug.return_value=dict(id=1,status='draft',job_opening_status='Active')
    response=app.test_client().get('/jobs/qa-draft',base_url='http://qa.hiregen.test')
    assert response.status_code==404
    assert b'qa-draft' not in response.data

@pytest.mark.parametrize('low,high,expected',[(None,None,'Salary not specified'),(0,100,'0 - 100'),(500,None,'From 500'),(None,900,'Up to 900')])
def test_employer_salary_fallback(app,low,high,expected):
    with app.app_context():
        html=app.jinja_env.get_template('widgets/salary_range.html').render(job=dict(min_salary=low,max_salary=high,salary_currency='$',salary_time_unit='Yearly'))
    assert expected in html
    assert 'None' not in html
