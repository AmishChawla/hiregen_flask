"""Exercise the actual blog route in isolation: no production imports or network."""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import socket
import pytest
from flask import Flask, abort, redirect, url_for, render_template
from jinja2 import DictLoader

ROOT=Path(__file__).resolve().parents[1]
ALIASES={
 'what-is-recruitment':'what-is-recruitment-process-funnel-and-metrics-with-formulas',
 'best-ai-recruitment-software-2026':'best-ai-recruitment-software-in-2026-ranked-and-compared',
 'ai-recruitment-statistics-2026':'ai-recruitment-statistics-2026-50-data-points-every-hr-leader-needs',
 'what-is-an-ats-complete-guide-2026':'what-is-an-ats-complete-guide-to-applicant-tracking-systems-2026',
}
@pytest.fixture
def blog(monkeypatch):
 def blocked(*args,**kwargs):raise AssertionError('Network forbidden')
 monkeypatch.setattr(socket.socket,'connect',blocked)
 app=Flask(__name__);app.config['TESTING']=True
 app.jinja_loader=DictLoader({'read_cms_post.html':'{{post.title}}|{{post.content|safe}}'})
 api=SimpleNamespace(get_post_by_slug=Mock(return_value=None))
 node=next(n for n in ast.parse((ROOT/'app.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='read_post')
 env=dict(app=app,api_calls=api,abort=abort,redirect=redirect,url_for=url_for,render_template=render_template)
 exec(compile(ast.Module(body=[node],type_ignores=[]),'isolated_blog_route','exec'),env)
 return app.test_client(),api

@pytest.mark.parametrize('old,new',ALIASES.items())
def test_permanent_redirect_without_api_call(blog,old,new):
 client,api=blog;response=client.get('/blog/'+old)
 assert response.status_code==301
 assert response.headers['Location']=='/blog/'+new
 api.get_post_by_slug.assert_not_called()

@pytest.mark.parametrize('slug',['unknown-blog-slug','ai-recruitment-software-cost-2026'])
def test_missing_article_returns_404(blog,slug):
 client,api=blog
 assert client.get('/blog/'+slug).status_code==404
 api.get_post_by_slug.assert_called_once_with(slug)

@pytest.mark.parametrize('value',[None,{},[]])
def test_empty_article_response_returns_404(blog,value):
 client,api=blog;api.get_post_by_slug.return_value=value
 assert client.get('/blog/missing').status_code==404

@pytest.mark.parametrize('slug',ALIASES.values())
def test_canonical_article_renders_without_redirect(blog,slug):
 client,api=blog;post={'title':'Article','slug':slug,'content':'&lt;p&gt;Existing article&lt;/p&gt;'}
 api.get_post_by_slug.return_value=post
 response=client.get('/blog/'+slug)
 assert response.status_code==200
 assert b'<p>Existing article</p>' in response.data
 assert post['content']=='&lt;p&gt;Existing article&lt;/p&gt;'

def test_redirect_target_renders(blog):
 client,api=blog;api.get_post_by_slug.return_value={'title':'Article','content':'Content'}
 response=client.get('/blog/what-is-recruitment',follow_redirects=True)
 assert response.status_code==200
 assert len(response.history)==1
 assert response.history[0].status_code==301

def test_null_content_does_not_crash(blog):
 client,api=blog;api.get_post_by_slug.return_value={'title':'Article','content':None}
 assert client.get('/blog/existing').status_code==200
