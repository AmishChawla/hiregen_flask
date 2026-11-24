"""Exercise quota errors without importing the real Flask app or API config."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock
import pytest
from job_quota_client import JobPostingLimitError, raise_job_limit_error

ROOT=Path(__file__).parents[1]

def extract(path,names,env):
    nodes=[]
    for node in ast.parse((ROOT/path).read_text()).body:
        if isinstance(node,ast.FunctionDef) and node.name in names:
            node.decorator_list=[]
            nodes.append(node)
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),str(path),'exec'),env)
    return env

@pytest.mark.parametrize('status,body,raises',[(409,{'detail':{'code':'active_job_limit_reached','message':'Close or unpublish a job.'}},True),(409,{'detail':'Other conflict'},False),(500,{},False),(200,{},False)])
def test_only_quota_conflict_becomes_form_error(status,body,raises):
    response=NS(status_code=status,json=lambda:body)
    if raises:
        with pytest.raises(JobPostingLimitError,match='Close or unpublish'):raise_job_limit_error(response)
    else:raise_job_limit_error(response)

@pytest.mark.parametrize('name,args',[('create_job_opening',dict(job_detail={},access_token='mock')),('update_job',dict(job_id=1,job_details={},access_token='mock'))])
def test_api_adapters_propagate_quota_rejection(name,args):
    response=NS(status_code=409,json=lambda:{'detail':{'code':'active_job_limit_reached','message':'Company limit: 50'}})
    errors=NS(HTTPError=OSError,ConnectionError=OSError,Timeout=OSError,RequestException=OSError)
    env=dict(requests=NS(post=Mock(return_value=response),put=Mock(return_value=response),exceptions=errors),constants=NS(BASE_URL='https://offline.invalid'),raise_job_limit_error=raise_job_limit_error,JobPostingLimitError=JobPostingLimitError)
    extract('api_calls.py',[name],env)
    with pytest.raises(JobPostingLimitError,match='50'):env[name](**args)

class Form:
    def __init__(self,**kw):
        self.publish=NS(data=True)
        self.save_draft=NS(data=False)
        self.preview=NS(data=False)
    def __getattr__(self,name):return NS(data='Mock input retained',errors=[])
    def validate_on_submit(self):return True

@pytest.mark.parametrize('name,template,args',[('add_post','add_post.html',()),('admin_edit_post','edit_post_form.html',('1',))])
def test_flask_rejection_preserves_bound_form(name,template,args):
    form=Form()
    api=NS(create_job_opening=Mock(side_effect=JobPostingLimitError('Company limit: 50')),
           update_job=Mock(side_effect=JobPostingLimitError('Company limit: 50')),
           get_job=lambda **kw:{},JobPostingLimitError=JobPostingLimitError)
    env=dict(forms=NS(AddJobOpening=lambda **kw:form),current_user=NS(id='mock',role='user',company={'id':1}),
             api_calls=api,render_template=lambda template,**kw:dict(template=template,**kw),datetime=__import__('datetime').datetime)
    extract('app.py',[name],env)
    result,code=env[name](*args)
    assert code==409 and result['template']==template
    assert result['form'] is form
    assert result['job_limit_error']=='Company limit: 50'


def test_jobs_page_uses_backend_usage():
    api=NS(get_user_all_job_openings=lambda **kw:{'jobs':[],'metrics':{}},get_company_job_usage=lambda **kw:{'active_jobs':12,'active_job_limit':50})
    env=dict(api_calls=api,current_user=NS(id='mock'),render_template=lambda template,**kw:kw)
    extract('app.py',['user_all_post'],env)
    assert env['user_all_post']()['job_usage']=={'active_jobs':12,'active_job_limit':50}
