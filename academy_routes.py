import os
from flask import Blueprint, render_template, abort, redirect, url_for, send_from_directory

academy_bp = Blueprint(
    'academy',
    __name__,
    url_prefix='/academy'
)

# Base path for static academy files (assets, dataset, resources)
ACADEMY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'academy')
TEMPLATES_ACADEMY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'academy')


@academy_bp.route('/', methods=['GET'])
def index():
    """Renders main Academy homepage"""
    return render_template('academy/index.html')


@academy_bp.route('/assets/<path:filename>', methods=['GET'])
def serve_assets(filename):
    """Serves course css, js, icons and static assets"""
    assets_dir = os.path.join(ACADEMY_DIR, 'assets')
    return send_from_directory(assets_dir, filename)


@academy_bp.route('/dataset/<path:filename>', methods=['GET'])
def serve_dataset(filename):
    """Serves dataset zip and sample data"""
    dataset_dir = os.path.join(ACADEMY_DIR, 'dataset')
    return send_from_directory(dataset_dir, filename)


@academy_bp.route('/resources/<path:filename>', methods=['GET'])
def serve_resources(filename):
    """Serves download resources (md, csv, xlsx, zip)"""
    resources_dir = os.path.join(ACADEMY_DIR, 'resources')
    return send_from_directory(resources_dir, filename)


@academy_bp.route('/<page_slug>', methods=['GET'])
def page(page_slug):
    """
    Renders top-level academy pages like course-map, glossary, resources, etc.
    Also handles 301 redirects if requested with .html
    """
    # Redirect .html requests to clean URL
    if page_slug.endswith('.html'):
        clean_slug = page_slug[:-5]
        return redirect(url_for('academy.page', page_slug=clean_slug), code=301)

    template_file = f'academy/{page_slug}.html'
    template_path = os.path.join(TEMPLATES_ACADEMY_DIR, f'{page_slug}.html')

    if os.path.exists(template_path):
        return render_template(template_file)
    
    abort(404)


@academy_bp.route('/<module_slug>/<lesson_slug>', methods=['GET'])
def lesson(module_slug, lesson_slug):
    """
    Renders lesson pages like module-4/lesson-4
    Also handles 301 redirects if requested with .html
    """
    # Redirect .html requests to clean URL
    if lesson_slug.endswith('.html'):
        clean_slug = lesson_slug[:-5]
        return redirect(url_for('academy.lesson', module_slug=module_slug, lesson_slug=clean_slug), code=301)

    template_file = f'academy/{module_slug}/{lesson_slug}.html'
    template_path = os.path.join(TEMPLATES_ACADEMY_DIR, module_slug, f'{lesson_slug}.html')

    if os.path.exists(template_path):
        return render_template(template_file)
    
    abort(404)
