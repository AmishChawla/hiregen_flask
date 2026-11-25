"""Contract checks for the redesign using isolated routes and mock data only."""
import subprocess
from bs4 import BeautifulSoup
import pytest
from redesign_preview import build_preview, APPLICANT

@pytest.fixture
def client():
 app=build_preview()
 with app.test_client() as c:
  c.get('/__preview/login/user')
  yield c

PAGES=['/user/job-openings','/user/job/applicants/168','/applicant-tracking','/setup-applicant-tracking','/employer/applicants/filter','/ai-chat','/profile','/__preview/careers','/jobs/test-job-junior-qa-engineer-not-real']
@pytest.mark.parametrize('path',PAGES)
def test_render_and_javascript(client,path,tmp_path):
 response=client.get(path)
 assert response.status_code==200
 soup=BeautifulSoup(response.data,'html.parser')
 assert soup.find('main')
 ids=[n['id'] for n in soup.select('[id]')]
 assert len(ids)==len(set(ids)),f'Duplicate IDs: {path}'
 for i,script in enumerate(soup.find_all('script')):
  if script.get('src') or script.get('type') in ('application/ld+json','application/json'):continue
  target=tmp_path/f'script{i}.js';target.write_text(script.text)
  result=subprocess.run(['node','--check',str(target)],capture_output=True,text=True)
  assert result.returncode==0,result.stderr

def test_search_form_contract(client):
 soup=BeautifulSoup(client.get('/employer/applicants/filter').data,'html.parser')
 names={n.get('name') for n in soup.select('input,select')}
 assert {'job_title','name','email','job_type','industry','application_start_date','application_end_date','available'}<=names
 response=client.post('/employer/applicants/filter',data={'name':'QA'})
 assert response.status_code in (200,302)

def test_profile_form_contract(client):
 soup=BeautifulSoup(client.get('/profile').data,'html.parser')
 assert len(soup.select('#saveBtn'))==1
 assert soup.select_one('form[enctype="multipart/form-data"]')
 assert soup.select_one('#cancelBtn')['type']=='button'
 assert {'profile_picture','company_logo','company_cover_image'}<={n.get('name') for n in soup.select('input[type=file]')}

def test_drawer_quoted_names(client):
 old=APPLICANT['applicant_name'];APPLICANT['applicant_name']="O'Neil <QA>"
 try:
  soup=BeautifulSoup(client.get('/user/job/applicants/168').data,'html.parser')
  handler=next(n.get('onclick') for n in soup.find_all('button') if (n.get('onclick') or '').startswith('openDrawer('))
  assert '\\u0027' in handler and '\\u003c' in handler
  assert len(soup.select('#applicantDrawer progress'))==6
 finally:APPLICANT['applicant_name']=old

def test_log_fields_preserved(client):
 soup=BeautifulSoup(client.get('/user/job/applicants/168').data,'html.parser')
 form=soup.select_one('#applicationLogForm')
 assert {'date','time','place','event_link','status','duration_minutes','score','reschedule_reason','notes','feedback'}<={n.get('name') for n in form.select('input,select,textarea')}

def test_navigation_respects_permissions(client):
 app=client.application;app.fixture_user.group={'permissions':['can_manage_jobs']}
 soup=BeautifulSoup(client.get('/user/job-openings').data,'html.parser')
 links=[a.text.strip() for a in soup.select('nav[aria-label="Main navigation"] a')]
 assert 'Jobs' in links
 assert 'Candidates' not in links and 'Team' not in links

@pytest.mark.parametrize('role',['guest','jobseeker','user'])
def test_public_job_role_controls(client,role):
 client.get('/__preview/login/'+role)
 soup=BeautifulSoup(client.get('/jobs/test-job-junior-qa-engineer-not-real').data,'html.parser')
 assert not soup.select('.hg-sidebar')
 assert bool(soup.select('#apply-btn'))==(role=='jobseeker')

@pytest.mark.parametrize('endpoint,path',[('user_dashboard','/dashboard'),('my_team','/my-team'),('employer_settings','/user/settings')])
def test_sidebar_destinations_render(client,endpoint,path):
 soup=BeautifulSoup(client.get('/user/job-openings').data,'html.parser')
 assert soup.select_one(f'nav[aria-label="Main navigation"] a[href="{path}"]')
 response=client.get(path)
 assert response.status_code==200
 assert b'/offline/'+endpoint.encode() not in response.data
