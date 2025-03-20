import csv
from datetime import datetime, timedelta
import json
import os
from io import StringIO, BytesIO
import csv
import ast
import PyPDF2
import stripe as stripe
from flask import Flask, render_template, redirect, url_for, flash, request, session, send_file, jsonify,g ,Response,send_from_directory,abort
import xml.etree.ElementTree as ET
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from jinja2 import Environment, FileSystemLoader
from werkzeug.utils import secure_filename
import uuid
import constants
import forms
import api_calls
import static_dropdowns
from constants import ROOT_URL
import google.generativeai as genai
from flask_wtf.csrf import CSRFProtect
import openai
from functools import wraps
from flask_cors import CORS
import phonenumbers
from phonenumbers.phonenumberutil import COUNTRY_CODE_TO_REGION_CODE
from typing import List, Dict, Any

app = Flask(__name__)
CORS(app, resources={r"/static/*": {"origins": "*"}})
app.config['SECRET_KEY'] = 'your_secret_key'
# csrf = CSRFProtect(app)
#TODO CHANGE TO 'hiregen.com' before deploying
# app.config['SERVER_NAME'] = 'localhost.com:5000'  # Base domain for subdomains
app.config['SERVER_NAME'] = 'hiregen.com'  
#TODO CHANGE TO '.hiregen.com' before deploying
# app.config['SESSION_COOKIE_DOMAIN'] = '.localhost.com'  # Leading dot to share session across subdomains
app.config['SESSION_COOKIE_DOMAIN'] = '.hiregen.com'  # Leading dot to share session across subdomains

app.config['SESSION_COOKIE_PATH'] = '/'
#TODO UNCOMMENT BEFORE DEPLOYING
app.config['SESSION_COOKIE_SECURE'] = True  # Uncomment if running on HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Adjust based on cross-domain requirements
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.init_app(app)
uploads_folder = 'uploads'
os.makedirs(uploads_folder, exist_ok=True)

media_folder = 'media'
os.makedirs(media_folder, exist_ok=True)

profile_pictures_folder = 'profile_pictures/'
os.makedirs(profile_pictures_folder, exist_ok=True)

password_reset_token = ""

####################### GEMINI MODEL CONFIG #########################
genai.configure(api_key=constants.GEMINI_APIKEY)
model = genai.GenerativeModel('gemini-pro')
openai.api_key = constants.OPEN_AI_API_KEY


@login_manager.user_loader
def load_user(user_id):
    user_from_session = session.get('user')
    if user_from_session is not None:
        # g[user] = user_from_session
        user = User(id=user_from_session.get('id'),
                    user_id=user_from_session.get('user_id'),
                    role=user_from_session.get('role'),
                    firstname=user_from_session.get('firstname'),
                    lastname=user_from_session.get('lastname'),
                    username=user_from_session.get('username'),
                    email=user_from_session.get('email'),
                    company=user_from_session.get('company'),
                    group=user_from_session.get('group'),
                    profile_picture=user_from_session.get('profile_picture'))
        return user
    else:
        return None


class User(UserMixin):
    def __init__(self, id, user_id, role, username, email, company, group, profile_picture, firstname=None, lastname=None):
        self.user_id = id
        self.id = user_id
        self.role = role
        self.firstname = firstname or ''
        self.lastname = lastname or ''
        self.username = username
        self.email = email
        self.company = company
        self.group = group
        self.profile_picture = profile_picture

    def has_permission(self, allowed_permissions):
        # Iterate over each item in the allowed permissions list
        for permission in allowed_permissions:
            # Check if the current permission exists in the group's permissions
            if permission in self.group.get('permissions', []):
                # If a match is found, return True immediately
                return True
        # If no match was found after iterating through all permissions, return False
        return False


def requires_any_permission(*required_permissions):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Convert unpacked arguments to a list if needed
            permissions_list = list(required_permissions) if not isinstance(required_permissions,
                                                                            list) else required_permissions

            # Check if the current user has any of the required permissions
            if not current_user.has_permission(permissions_list):
                # Redirect to a login page or show an error message
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_pdf():
    form = forms.UploadForm()
    if form.validate_on_submit():
        uploaded_files = request.files.getlist('files')
        print(len(uploaded_files))
        empty_folder(uploads_folder)
        file_list = []
        print(len(uploaded_files))
        for file in uploaded_files:
            # Ensure the file has a secure filename
            filename = secure_filename(file.filename)
            # Save the file to a designated folder
            file_path = 'uploads/' + filename
            print(file_path)
            file.save(file_path)
            file_list.append(('pdf_files', (filename, open(file_path, 'rb'))))

        response = api_calls.dashboard(file_list, current_user.id)
        print(response.json())
        if response.status_code == 200:
            result = response.json()
            # Extract the CSV data from the response
            csv_data = result.get('extracted_data', [])

            # Use StringIO to create a file-like object for the csv.reader
            # csv_file = StringIO(csv_data)

            # Parse the CSV data into a list of lists
            # csv_reader = list(csv.reader(csv_file))
            #
            # The first row contains headers, and the rest are data rows
            # headers = csv_reader[0]
            # data_rows = csv_reader[1:]
            # Process the uploaded files or redirect to a new page
            xml_data = result.get('xml_file')
            return render_template('result.html', csv_data=csv_data, xml_data=xml_data)

    return render_template('upload_pdf.html', form=form)


def empty_folder(folder):
    # Remove all files in the uploads folder
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        try:
            if os.path.isfile(file_path):
                with open(file_path, 'wb'):
                    pass  # This opens and immediately closes the file to release any locks
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")


@app.route("/employer/login", methods=['GET', 'POST'])
def login():
    session.pop('_flashes', None)
    print('trying')
    if current_user.is_authenticated:
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('user_dashboard') if current_user.company else url_for('company_register'))

    next_page = request.args.get('next') or request.form.get('next')
    print(f"Next Page Before Validation: {next_page}")

    form = forms.LoginForm()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        response = api_calls.user_login(email, password)

        if response is not None and response.status_code == 200:
            data = response.json()
            id = data.get('id')
            token = data.get('access_token')
            role = data.get('role')
            firstname = data.get('firstname')
            lastname = data.get('lastname')
            username = data.get('username')
            email = data.get('email')
            company = data.get('company', {})
            group = data.get('group', {})
            profile_picture = data['profile_picture']

            user = User(id=id, user_id=token, role=role, firstname=firstname, lastname=lastname, username=username, email=email, company=company,
                        group=group, profile_picture=profile_picture)
            login_user(user)
            session['user'] = {
                'id': id,
                'user_id': token,
                'role': role,
                'firstname': firstname,
                'lastname': lastname,
                'username': username,
                'email': email,
                'company': company,
                'group':group,
                'profile_picture': profile_picture,
            }
            next_page = next_page or (url_for('user_dashboard') if user.company else url_for('company_register'))
            print(f"Redirecting to: {next_page}")
            return redirect(next_page)


        elif response.status_code == 400:
            result = response.json()
            message = result["detail"]
            flash(message, category='error')
        else:
            # Handle the case where the response is None or the status code is not 200
            print("Error: Response is None or status code is not 200")
            flash('Login unsuccessful. Please check email and password.', category='error')

    return render_template('login.html', form=form)

@app.route('/google-login')
def google_login():
    return redirect(constants.AUTHORIZATION_BASE_URL + '?response_type=code&client_id=' + constants.GOOGLE_CLIENT_ID +
                    '&redirect_uri=' + constants.REDIRECT_URI + '&scope=email%20profile')

@app.route('/callback')
def callback():
    import requests
    error = request.args.get('error')
    if error:
        # Handle the error, e.g., log it or redirect to an error page
        print(f"OAuth2 Error: {error}")
        return redirect(url_for('login'))
    code = request.args.get('code')
    params = {
        'code': code,
        'client_id': constants.GOOGLE_CLIENT_ID,
        'client_secret': constants.GOOGLE_CLIENT_SECRET,
        'redirect_uri': constants.REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    token_response = requests.post(constants.TOKEN_URL, data=params)
    access_token = token_response.json().get('access_token')
    user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo?alt=json'
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info = user_info_response.json()
    print(user_info)
    data = api_calls.get_user_from_google_login(user_info=user_info)

    id = data.get('id')
    token = data.get('access_token')
    role = data.get('role')
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    username = data.get('username')
    email = data.get('email')
    profile_picture = data.get('profile_picture')
    print(profile_picture)
    company = data.get('company', {})
    group = data.get('group', {})

    user = User(id=id, user_id=token, role=role, firstname=firstname, lastname=lastname, username=username, email=email, company=company,
                group=group, profile_picture=profile_picture)
    login_user(user)
    session['user'] = {
        'id': id,
        'user_id': token,
        'role': role,
        'firstname': firstname,
        'lastname': lastname,
        'username': username,
        'email': email,
        'company': company,
        'group': group,
        'profile_picture': profile_picture
    }
    if current_user.company is not None:
        return redirect(url_for('user_dashboard'))
    else:
        return redirect(url_for('company_register'))


def verify_recaptcha(token):
    import requests
    secret_key = "6LfjmMUqAAAAAJgO28h7Lb3vgzG3ed8YBhRacryN"  # Replace with your Secret Key
    url = "https://www.google.com/recaptcha/api/siteverify"
    data = {
        "secret": secret_key,
        "response": token
    }
    response = requests.post(url, data=data)
    result = response.json()
    return result.get("success", False)  # Returns True if valid

@app.route("/register", methods=['GET', 'POST'])
def register():
    session.pop('_flashes', None)


    form = forms.RegisterForm()
    print("outside")
    if form.validate_on_submit():
        firstname= form.firstname.data
        lastname = form.lastname.data
        phone_number = form.phone_number.data
        email = form.email.data
        password = form.password.data

        recaptcha_token = request.form.get('g-recaptcha-response')
        recaptcha_success = verify_recaptcha(recaptcha_token)

        if recaptcha_success:

            response = api_calls.user_register(firstname, lastname, phone_number, email, password)
            print("inside")
            if response.status_code == 200:
                response = api_calls.user_login(email, password)
                if response is not None and response.status_code == 200:
                    data = response.json()
                    token = data.get('access_token')
                    id=data.get('id')
                    role = data.get('role')
                    firstname = data.get('firstname')
                    lastname = data.get('lastname')
                    username = data.get('username')
                    email = data.get('email')
                    company = data.get('company', {})
                    group = data.get('group', {})
                    profile_picture = data['profile_picture']

                    user = User(id=id,user_id=token, firstname=firstname, lastname=lastname,role=role, username=username, email=email,
                                company=company,group=group,
                                profile_picture=profile_picture)
                    login_user(user)
                    session['user'] = {
                        'id': id,
                        'user_id': token,
                        'role': role,
                        'firstname': firstname,
                        'lastname': lastname,
                        'username': username,
                        'email': email,
                        'company': company,
                        'group': group,
                        'profile_picture': profile_picture
                    }
                flash('Registration Successful', category='info')
                return redirect((url_for('create_subscription', plan_id=1)))  # Hardcoded value for free plan
            elif response.status_code == 400:
                result = response.json()
                message = result["detail"]
                flash(message, category='error')

            else:
                flash('Registration unsuccessful. Please check username, email and password.', category='error')
        else:
            flash('Registration unsuccessful. Please check username, email and password.', category='error')

    return render_template('register.html', form=form)


@app.route("/dashboard")
@login_required
def user_dashboard():
    stats = api_calls.get_stats(access_token=current_user.id)
    total_jobs = stats["total_jobs"]
    total_views = stats["total_views"]
    applicants_count = stats["applicants_count"]
    in_progress_jobs = stats["in_progress_jobs"]
    statuses = stats["statuses"]

    latest_jobs = api_calls.get_user_all_job_openings(maximum_posts=5, access_token=current_user.id)


    return render_template('dashboard.html', total_jobs=total_jobs, total_views=total_views, applicants_count=applicants_count, in_progress_jobs=in_progress_jobs, statuses=statuses, latest_jobs=latest_jobs)


@app.route("/admin/admin-dashboard")
@requires_any_permission("manage_user", "list_of_users", "list_of_sites", "owner_email_setup",
                     "manage_subscription_plans", "order_history")
@login_required
def admin_dashboard():
    stats = api_calls.get_admin_stats_for_dashboard(current_user.id)

    return render_template('admin_dashboard.html', stats=stats)


@app.route("/admin/settings")
@requires_any_permission("manage_user", "list_of_users", "list_of_sites", "owner_email_setup",
                     "manage_subscription_plans", "order_history")
@login_required
def setting():
    return render_template('setting.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('Logout successful!', 'success')
    return redirect(url_for('login'))


@app.route('/result/<result>')
@login_required
def result():
    result = session.get('result', {})
    return render_template('result.html', result=result)


@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    is_company_registered = False
    empty_folder(uploads_folder)
    empty_folder(profile_pictures_folder)

    form = forms.EmployerProfileForm()

    # Get user data from API or database
    response = api_calls.get_user_profile(current_user.id)
    result = response.json()
    print(result)

    # Populate the fields with data
    if request.method == 'GET':
        form.firstname.data = result["firstname"]
        form.lastname.data = result["lastname"]
        form.phone_number.data = result['phone_number']
        form.username.data = result["username"]
        form.email.data = result["email"]

        current_plan=result.get('current_plan')
        company = result.get('company', {})
        if company:
            is_company_registered = True
            form.company_name.data = company.get('name', '')
            form.company_location.data = company.get('location', '')
            form.company_website.data = company.get('company_website', '')
            form.company_description.data = company.get('company_description', '')

    # On form submit, process the data
    if form.validate_on_submit():
        # Update user and company details
        profile_data = {
            'firstname': form.firstname.data,
            'lastname': form.lastname.data,
            'phone_number': form.phone_number.data,
            'username': form.username.data,
            'email': form.email.data,
            'profile_picture': form.profile_picture.data,
            'company_name': form.company_name.data,
            'company_location': form.company_location.data,
            'company_website': form.company_website.data,
            'company_description': form.company_description.data,
            'company_logo': form.company_logo.data,
        }

        profile_picture = form.profile_picture.data or None
        if profile_picture:
            profile_picture_filename = secure_filename(profile_picture.filename)
            # Save the file to a designated folder
            profile_picture_path = 'profile_pictures/' + profile_picture_filename
            print(profile_picture_path)
            profile_picture.save(profile_picture_path)
            profile_picture = (profile_picture_filename, open(profile_picture_path, 'rb'))


        company_logo = form.company_logo.data or None
        if company_logo:
            company_logo_filename = secure_filename(company_logo.filename)
            # Save the file to a designated folder
            company_logo_path = 'uploads/' + company_logo_filename
            print(company_logo_path)
            company_logo.save(company_logo_path)
            company_logo = (company_logo_filename, open(company_logo_path, 'rb'))


        response = api_calls.update_user_profile(token=current_user.id, firstname=profile_data.get('firstname'),lastname=profile_data.get('lastname'),phone_number=profile_data.get('phone_number'),username=profile_data.get('username'),email=profile_data.get('email'),profile_picture=profile_picture,company_name=profile_data.get('company_name'),company_location=profile_data.get('company_location'),company_website=profile_data.get('company_website'),company_description=profile_data.get('company_description'),company_logo=company_logo)

        if response.status_code == 200:
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Failed to update profile. Please try again.', 'danger')

    return render_template('profile.html', form=form, current_plans=result.get('current_plans', []),
                           profile_picture=result.get('profile_picture'), company=result.get('company'), is_company_registered=is_company_registered, current_plan=current_plan)


@app.route("/admin/users")
@requires_any_permission("list_of_users")
@login_required
def list_of_users():
    form = forms.AdminAddUserForm()

    response = api_calls.get_all_users(
        current_user.id,
    )

    if response.status_code == 200:
        users = response.json()

    else:
        abort(response.status_code)

    return render_template('list_of_users.html', result=users, form=form)


@app.route("/admin/sites")
@requires_any_permission("list_of_users")
@login_required
def list_of_sites():
    ITEMS_PER_PAGE = 5
    # Fetch all users

    response = api_calls.get_admin_all_sites(
        current_user.id,
    )

    if response.status_code == 200:
        sites = response.json()

    else:
        abort(response.status_code)

    return render_template('list_of_sites.html', result=sites)


@app.route("/admin/login", methods=['GET', 'POST'])
def admin_login():
    session.pop('_flashes', None)
    print('trying')
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))

    form = forms.LoginForm()
    print(form.validate_on_submit())

    if form.validate_on_submit():

        email = form.email.data
        password = form.password.data
        response = api_calls.admin_login(email, password)

        # if response.status_code == 200:
        #     data = response.json()
        #     token = data.get('access_token')
        #     role = data.get('role')
        #     username = data.get('username')
        #     email = data.get('email')
        #     services = data.get('services')
        #     company = data.get('company')

        if (response.status_code == 200):
            id = response.json().get('id')
            token = response.json().get('access_token')
            role = response.json().get('role')
            username = response.json().get('username')
            email = response.json().get('email')
            group = response.json().get('group', {})
            profile_picture = f"{ROOT_URL}/{response.json()['profile_picture']}"
            user = User(id=id, user_id=token, role=role, username=username, email=email, company={},group=group,
                        profile_picture=profile_picture)
            login_user(user)
            session['user'] = {
                'id': id,
                'user_id': token,
                'role': role,
                'username': username,
                'email': email,
                'company': {},
                'group': group,
                'profile_picture': profile_picture
            }

            return redirect(url_for('admin_dashboard'))
        elif response.status_code == 400:
            result = response.json()
            message = result["detail"]
            flash(message, category='error')
        else:
            flash('Login unsuccessful. Please check email and password.', category='error')

    return render_template('admin_login.html', form=form)


@app.route("/admin/add-user", methods=['GET', 'POST'])
@requires_any_permission("manage_user")
@login_required
def add_user():
    form = forms.AdminAddUserForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        role = form.role.data
        security_group = form.security_group.data
        response = api_calls.add_user(username, email, password, role, security_group, current_user.id)
        print(response.status_code)
        if (response.status_code == 200):
            flash('Registration Successful', category='info')
            return redirect(url_for('admin_dashboard'))
        else:
            abort(response.status_code)

    return render_template('admin_add_user.html', form=form)


@app.route("/admin/trash-user/<user_id>", methods=['GET', 'POST'])
@requires_any_permission("manage_user")
@login_required
def admin_trash_user(user_id):
    result = api_calls.admin_trash_user(access_token=current_user.id, user_id=user_id)
    if (result.status_code == 200):
        print(result)
        return redirect(url_for('list_of_users'))
    else:
        abort(result.status_code)


@app.route("/admin/delete-user/<user_id>", methods=['GET', 'POST'])
@requires_any_permission("manage_user")
@login_required
def admin_delete_user_permanently(user_id):
    result = api_calls.admin_delete_user_permanently(access_token=current_user.id, user_id=user_id)
    if (result.status_code == 200):
        print(result)
        return redirect(url_for('list_of_users'))
    else: abort(result.status_code)


@app.route("/admin/restore-user/<user_id>", methods=['GET', 'POST'])
@requires_any_permission("manage_user")
@login_required
def admin_restore_user(user_id):
    result = api_calls.admin_restore_user(access_token=current_user.id, user_id=user_id)
    if (result.status_code == 200):
        print(result)
        return redirect(url_for('list_of_users'))
    else: abort(result.status_code)

@app.route("/admin/view-user-profile/<user_id>", methods=['GET', 'POST'])
@requires_any_permission("manage_user")
@login_required
def admin_view_user_profile(user_id):
    profile = api_calls.admin_get_any_user(access_token=current_user.id, user_id=user_id)

    return render_template('admin_view_user_profile.html', profile=profile, profile_picture=profile.get('profile_picture'), company=profile.get('company'))


@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    session.clear()
    flash('Logout successful!', 'success')
    return redirect(url_for('admin_login'))


@app.route("/profile/update_password/", methods=['GET', 'POST'])
@login_required
def user_password_update():
    form = forms.UserPasswordUpdateForm()

    if form.validate_on_submit():

        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_new_password = form.confirm_new_password.data
        response = api_calls.update_user_password(current_password=current_password, new_password=new_password,
                                                  confirm_new_password=confirm_new_password,
                                                  access_token=current_user.id)
        print(response.status_code)
        if response.status_code == 200:
            flash('Password Updated Successfully', category='info')
            if current_user.role == 'user':
                return redirect(url_for('profile'))
            else:
                return redirect(url_for('admin_dashboard'))
        else:
            flash('Unsuccessful. Please check password.', category='error')
    return render_template('user_password_update.html', form=form)


@app.route("/forget-password", methods=['GET', 'POST'])
def forgot_password():
    form = forms.ForgetPasword()

    if form.validate_on_submit():
        email = form.email.data
        response = api_calls.forgot_password(email)
        print(response.status_code)
        if (response.status_code == 200):
            return render_template('mail_success.html')
    return render_template('forgot_password.html', form=form)


@app.route("/reset-password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    form = forms.ResetPasswordForm()
    if form.validate_on_submit():
        new_password = form.new_password.data
        response = api_calls.reset_password(token, new_password)
        print(response.status_code)
        if (response.status_code == 200):
            flash("Password updated successfully")
            return redirect(url_for('logout'))
    return render_template('reset_password.html', form=form, token=token)


@app.route("/user/history", methods=['GET', 'POST'])
@login_required
def user_history():
    response = api_calls.get_user_profile(access_token=current_user.id)
    if response.status_code == 200:
        result = response.json()
        username = result["username"]
        email = result["email"]
        role = result["role"]
        resume_data = []
        # data_list = []
        # for index in range(len(result["resume_data"])):
        #     extracted_data = result["resume_data"][index]["extracted_data"]
        #     data_list.append(extracted_data)
    # template = env.get_template('admin_view_user_profile.html')
    # output = template.render(csv_files=csv_files, email=email, role = role, username=username)
    # print(resume_data[0]["upload_datetime"])
    return render_template('admin_view_user_profile.html', email=email, role=role,
                           username=username, resume_data=resume_data)


@app.route("/admin/edit-user-profile/<user_id>", methods=['GET', 'POST'])
@requires_any_permission("manage_user")
@login_required
def admin_edit_user_profile(user_id):
    form = forms.AdminEditUserForm()
    result = api_calls.admin_get_any_user(access_token=current_user.id, user_id=user_id)
    username = result["username"]
    role = result["role"]
    status = result["status"]
    service_response = api_calls.services()


    if form.validate_on_submit():
        new_username = form.username.data
        new_role = form.role.data
        new_status = form.status.data

        response = api_calls.admin_edit_any_user(access_token=current_user.id, user_id=user_id,
                                                 username=new_username, role=new_role, status=new_status)

        if response.status_code == 200:
            return redirect(url_for('admin_edit_user_profile', user_id=user_id))
        else:
            abort(response.status_code)

    form.username.data = username
    form.role.data = role
    form.status.data = status

    return render_template('edit_form.html', status=status, role=role, username=username, form=form,
                           user_id=user_id)

########################################################################## COMPANIES ###############################################################3

@app.route("/admin/companies", methods=['GET', 'POST'])
@login_required
def list_of_companies():
    response = api_calls.admin_get_all_companies()
    if (response.status_code == 200):
        result = response.json()
        print(result)
    return render_template('list_of_companies.html', result=result)


@app.route("/admin/delete-company/<company_id>", methods=['GET', 'POST'])
@login_required
def admin_delete_company(company_id):
    result = api_calls.admin_delete_company(company_id=company_id)
    if (result.status_code == 200):
        return redirect(url_for('list_of_companies'))


@app.route("/admin/edit-company/<company_id>", methods=['GET', 'POST'])
@login_required
def admin_edit_company(company_id):
    form = forms.AdminEditCompanyForm()
    result = api_calls.admin_get_any_company(company_id)
    name = result["name"]
    website_url = result["website_url"]

    if form.validate_on_submit():
        # Update user information
        name = form.name.data
        website_url = form.website_url.data
        print(location)

        response = api_calls.admin_edit_any_company(company_id=company_id,
                                                    name=name, website_url=website_url)
        print(response.status_code)
        if response.status_code == 200:
            return redirect(url_for('list_of_companies'))

    # Prefill the form fields with user information
    form.name.data = name
    form.website_url.data = website_url

    return render_template('admin_edit_company.html', website_url=website_url, name=name, form=form, company_id=company_id)


@app.route("/company-register", methods=['GET', 'POST'])
def company_register():
    form = forms.CompanyRegisterForm()
    print("outside")
    if form.validate_on_submit():

        name = form.name.data
        website_url = form.website_url.data
        location = form.location.data
        company_subdomain = form.company_subdomain.data
        description = form.description.data

        empty_folder(uploads_folder)
        file = form.company_logo.data

        filename = secure_filename(file.filename)
        # Save the file to a designated folder
        file_path = 'uploads/' + filename
        print(file_path)
        file.save(file_path)
        payload = {'company_logo': (filename, open(file_path, 'rb'))}

        response = api_calls.company_register(name, website_url,logo=payload,location=location, description=description,company_subdomain=company_subdomain, access_token=current_user.id)
        print("inside")

        if (response.status_code == 200):
            flash('Registration Successful', category='info')
            if (current_user.role == 'user'):
                current_user.company = dict(response.json())
                session['user']['company'] = dict(response.json())

                return redirect(url_for('user_dashboard'))
            else:
                return redirect(url_for('list_of_companies'))
        else:
            flash('Registration unsuccessful.', category='error')

    return render_template('company_register.html', form=form)

@app.route('/admin/companies/<company_id>', methods=['GET', 'POST'])
def company_details(company_id):
    result = api_calls.get_company_details(company_id=company_id)

    name = result["name"]
    location = result["location"]
    description = result["description"]
    website_url = result["website_url"]

    return render_template('company_details.html', name=name, location=location, description=description, website_url=website_url)



@app.route('/companies/<company_slug>', methods=['GET', 'POST'])
def company_details_by_company_slug(company_slug):
    result = api_calls.get_company_details_by_slug(company_slug=company_slug)

    company_id = result["id"]
    jobs_by_company = api_calls.get_jobs_by_company_id(company_id=company_id)

    return render_template('company_details.html', company=result, job_posts=jobs_by_company)

@app.route('/', subdomain="<company_subdomain>", methods=['GET', 'POST'])
def company_details_by_company_subdomain(company_subdomain):
    # Get the company details based on the subdomain
    result = api_calls.get_company_details_by_subdomain(company_subdomain=company_subdomain)

    # Retrieve jobs associated with the company
    company_id = result["id"]
    jobs_by_company = api_calls.get_jobs_by_company_id(company_id=company_id)

    # Render the template with company details and job postings
    return render_template('company_details.html', company=result, job_posts=jobs_by_company)



######################################## resume history ##########################################################################
@app.route("/admin/resume-history", methods=['GET', 'POST'])
@login_required
def resume_history():
    response = api_calls.admin_get_resume_history()
    if response.status_code == 200:
        result = response.json()
        return render_template('resume_history.html', result=result)


####################################### trash ##########################################################################
@app.route("/admin/trash")
@requires_any_permission("manage_user")
@login_required
def trash():
    response = api_calls.get_trash_users(
        current_user.id,
    )

    if response.status_code == 200:
        users = response.json()

    else:
        abort(response.status_code)

    return render_template('trash.html', result=users)


####################################### EMAIL SETUP ##########################################################################
@app.route("/admin/email-setup", methods=['GET', 'POST'])
@requires_any_permission("owner_email_setup")
@login_required
def admin_email_setup():
    result = api_calls.admin_get_email_setup(access_token=current_user.id)
    form = forms.EmailFunctionalityForm()

    if result.status_code == 200:
        email_details = result.json()
        smtp_server = email_details.get("smtp_server")
        smtp_port = email_details.get("smtp_port")
        smtp_username = email_details.get("smtp_username")
        smtp_password = email_details.get("smtp_password")
        sender_email = email_details.get("sender_email")
        if form.validate_on_submit():

            new_smtp_server = form.smtp_server.data
            new_smtp_port = form.smtp_port.data
            new_smtp_username = form.smtp_username.data
            new_smtp_password = form.smtp_password.data
            new_sender_email = form.sender_email.data
            # Ensure the file is included in the request
            response = api_calls.admin_update_email_setup(access_token=current_user.id,
                                                          smtp_server=new_smtp_server, smtp_port=new_smtp_port,
                                                          smtp_username=new_smtp_username,
                                                          smtp_password=new_smtp_password,
                                                          sender_email=new_sender_email)
            if response.status_code == 200:
                return redirect(url_for('admin_email_setup'))
            else:
                abort(response.status_code)

        form.smtp_server.data = smtp_server
        form.smtp_port.data = smtp_port
        form.smtp_username.data = smtp_username
        form.smtp_password.data = smtp_password
        form.sender_email.data = sender_email

    return render_template('email_form.html', form=form)


################################################################ PLANS ########################################################################
@app.route("/admin/settings/plans", methods=['GET', 'POST'])
@requires_any_permission("manage_subscription_plans")
@login_required
def list_of_plans():
    result = api_calls.get_all_plans()
    print(result)
    return render_template('admin_plan_page.html', plans=result)


@app.route('/admin/settings/add-plan', methods=['GET', 'POST'])
@requires_any_permission("manage_subscription_plans")
@login_required
def add_plan():
    if request.method == 'POST':
        data = request.get_json()

        plan_name = data.get('plan_name')
        duration = data.get('duration')
        email = data.get('email')  # Not used in processing but included in form
        price = data.get('price', 0.0)
        currency = data.get('currency', 'USD')
        job_postings = data.get('job_postings', 0)

        # Features toggle
        features = {
            "ai_candidate_matching": data.get("ai_candidate_matching", False),
            "ai_based_resume_ranking": data.get("ai_based_resume_ranking", False),
            "applicant_tracking": data.get("applicant_tracking", False),
            "resume_parsing": data.get("resume_parsing", False),
            "analytics_and_reports": data.get("analytics_reports", False),
            "interview_scheduling": data.get("interview_scheduling", False),
            "multi_user_access": data.get("multi_user_access", False),
            "branded_careers_page": data.get("branded_careers_page", False),
        }

        # Call API to create plan
        result = api_calls.create_plan(
            plan_name=plan_name,
            duration=1, #months
            price=price,
            job_postings=job_postings,
            features=features
        )

        if result:
            return jsonify({"message": "Plan created successfully!"}), 201
        else:
            return jsonify({"error": "Failed to create plan."}), 400

    return render_template('add_plan.html')


@app.route("/admin/settings/update-plan/<plan_id>", methods=['GET', 'POST'])
@requires_any_permission("manage_subscription_plans")
@login_required
def update_plan(plan_id):
    form = forms.AddPlan()
    result = api_calls.get_plan_by_id(plan_id)
    name = result["plan_type_name"]
    duration = result["time_period"]
    fees = result["fees"]
    num_resume_parse = result["num_resume_parse"]
    plan_details = result["plan_details"]

    if form.validate_on_submit():
        # Update user information
        name = form.name.data
        duration = form.duration.data
        fees = 0 if form.is_free.data else form.fees.data
        num_resume_parsing = 'unlimited' if form.unlimited_resume_parsing.data else form.num_resume_parsing.data
        plan_details = form.plan_details.data
        result = api_calls.update_plan(plan_id=plan_id, plan_name=name, time_period=duration, fees=fees,
                                       num_resume_parse=num_resume_parsing, plan_details=plan_details)
        if result:
            return redirect(url_for('list_of_plans'))
    else:
        print(form.errors)

    # Prefill the form fields with user information
    form.name.data = name
    form.duration.data = duration
    form.plan_details.data = plan_details
    if fees == 0:
        form.is_free.data = True
    else:
        form.fees.data = fees
    if num_resume_parse == 'unlimited':
        form.unlimited_resume_parsing.data = True
    else:
        form.num_resume_parsing.data = num_resume_parse

    return render_template('update_plan.html', form=form, plan_id=plan_id)


@app.route("/admin/settings/plans/delete-plan/<plan_id>", methods=['GET', 'POST'])
@requires_any_permission("manage_subscription_plans")
@login_required
def delete_plan(plan_id):
    result = api_calls.delete_plan(plan_id=plan_id)
    if result:
        return redirect(url_for('list_of_plans'))


@app.route("/pricing", methods=['GET', 'POST'])
def user_view_plan():
    result = api_calls.get_all_plans()
    return render_template('pricing.html', pricing=result)


@app.route('/admin/posts')
@login_required
def all_post():
    result = api_calls.get_all_posts()
    if result is None:
        result = []  # Set result to an empty list
    print(result)

    return render_template('all_posts.html', result=result)

####################################### POSTS #####################################################################
@app.route('/admin/job-openings')
@requires_any_permission("manage_user")
@login_required
def admin_all_jobs():
    result = api_calls.get_all_job_openings_for_admin(access_token=current_user.id)
    if result is None:
        result = []  # Set result to an empty list

    return render_template('admin/admin_all_jobs.html', result=result)



@app.route('/user/job-openings')
@requires_any_permission("manage_posts")
@login_required
def user_all_post():
    result = api_calls.get_user_all_job_openings(access_token=current_user.id)
    if result is None:
        result = []  # Set result to an empty list

    return render_template('user_all_post.html', result=result)
#['applied', 'shortlisted', 'assessment', 'interview', 'rejected', 'selected']
@app.route('/user/job/applicants/<job_id>')
@requires_any_permission("manage_posts")
@login_required
def job_applicants(job_id):
    result = api_calls.get_job_applicants(access_token=current_user.id, job_id=job_id)
    statuses = api_calls.get_applicant_trackers(access_token=current_user.id)
    if statuses is not None:
        job_statuses = [item['job_status'] for item in statuses]
    if result is None:
        result = []  # Set result to an empty list
    if statuses is None:
        return render_template('cms/job_openings/job_applicants_2.html', result=result)

    print(result)
    print(statuses)
    return render_template('cms/job_openings/job_applicants_3.html', result=result, statuses=job_statuses)


@app.route('/applicant-tracking')
@requires_any_permission("manage_posts")
@login_required
def all_applicants():
    job_types = static_dropdowns.job_types
    industries = static_dropdowns.industries
    result = api_calls.get_all_applicants(access_token=current_user.id)
    statuses = api_calls.get_applicant_trackers(access_token=current_user.id)
    if result is None:
        result = []  # Set result to an empty list
    if statuses is None:
        statuses = [
            {
                "id": 1,
                "name": "Applied",
                "description": "applied",
                "job_status": "applied",
                "on_jobseeker_apply": True
            },
            {
                "id": 2,
                "name": "Shortlisted",
                "description": "shortlisted",
                "job_status": "shortlisted",
                "on_jobseeker_apply": False
            },
            {
                "id": 3,
                "name": "Assessment",
                "description": "assessment",
                "job_status": "assessment",
                "on_jobseeker_apply": False
            },
            {
                "id": 4,
                "name": "Interview",
                "description": "interview",
                "job_status": "interview",
                "on_jobseeker_apply": False
            },
            {
                "id": 5,
                "name": "Rejected",
                "description": "rejected",
                "job_status": "rejected",
                "on_jobseeker_apply": False
            },
            {
                "id": 6,
                "name": "Selected",
                "description": "selected",
                "job_status": "selected",
                "on_jobseeker_apply": False
            }
        ]


    return render_template('cms/job_openings/job_applicants.html', result=result, statuses=statuses, job_types=job_types, industries=industries)



@app.route('/admin/applicant-tracking')
@requires_any_permission("manage_user")
@login_required
def all_applicants_for_admin():
    result = api_calls.get_all_applicants_for_admin(access_token=current_user.id)
    statuses = api_calls.get_applicant_trackers(access_token=current_user.id)
    if result is None:
        result = []  # Set result to an empty list
    if statuses is None:
        statuses = [
            {
                "id": 1,
                "name": "Applied",
                "description": "applied",
                "job_status": "applied",
                "on_jobseeker_apply": True
            },
            {
                "id": 2,
                "name": "Shortlisted",
                "description": "shortlisted",
                "job_status": "shortlisted",
                "on_jobseeker_apply": False
            },
            {
                "id": 3,
                "name": "Assessment",
                "description": "assessment",
                "job_status": "assessment",
                "on_jobseeker_apply": False
            },
            {
                "id": 4,
                "name": "Interview",
                "description": "interview",
                "job_status": "interview",
                "on_jobseeker_apply": False
            },
            {
                "id": 5,
                "name": "Rejected",
                "description": "rejected",
                "job_status": "rejected",
                "on_jobseeker_apply": False
            },
            {
                "id": 6,
                "name": "Selected",
                "description": "selected",
                "job_status": "selected",
                "on_jobseeker_apply": False
            }
        ]


    return render_template('admin/admin_all_applicants.html', result=result, statuses=statuses)


@app.route('/admin/jobseekers')
@requires_any_permission("manage_user")
@login_required
def admin_all_jobseekers():
    result = api_calls.get_all_jobseekers_for_admin(access_token=current_user.id)
    if result is None:
        result = []  # Set result to an empty list

    return render_template('admin/admin_all_jobseekers.html', result=result)



# @app.route('/<username>/jobs', methods=['GET', 'POST'])
# def user_post_list(username):
#     toast = 'null'
#     form = forms.SubscribeToNewsletterForm()
#     result = api_calls.get_user_job_opening_by_username(username=username)
#
#     if result is None:
#         result = []  # Set result to an empty list
#
#     response = []
#
#     if form.validate_on_submit():
#         print('inside validating')
#         name = form.name.data
#         email = form.email.data
#         print('sending call')
#         response_status = api_calls.subscribe_to_newsletter(name=name, email=email, username=username)
#         if response_status == 200:
#             return redirect(url_for('user_post_list', username=username, toast='new_sub'))
#         elif response_status == 409:
#             return redirect(url_for('user_post_list', username=username, toast='already_sub'))
#         else:
#             return redirect(url_for('user_post_list', username=username, toast='null'))
#
#     return render_template('user_post_list.html', result=result, response=response, form=form, username=username, toast=toast)


@app.route('/jobs',subdomain='<company_subdomain>', methods=['GET', 'POST'])
def user_post_list_by_company_subdomain(company_subdomain):
    toast = 'null'
    form = forms.SubscribeToNewsletterForm()
    result = api_calls.get_job_opening_by_company_subdomain(company_subdomain=company_subdomain)

    if result is None:
        result = []  # Set result to an empty list

    response = []

    if form.validate_on_submit():
        print('inside validating')
        name = form.name.data
        email = form.email.data
        print('sending call')
        response_status = api_calls.subscribe_to_newsletter(name=name, email=email, username=username)
        if response_status == 200:
            return redirect(url_for('user_post_list_by_company_subdomain', company_subdomain=company_subdomain, toast='new_sub'))
        elif response_status == 409:
            return redirect(url_for('user_post_list_by_company_subdomain', company_subdomain=company_subdomain, toast='already_sub'))
        else:
            return redirect(url_for('user_post_list_by_company_subdomain', company_subdomain=company_subdomain, toast='null'))

    return render_template('user_post_list.html', result=result, response=response, form=form, toast=toast)



@app.route("/admin/delete-job/<job_id>", methods=['GET', 'POST'])
@login_required
def admin_delete_job(job_id):
    result = api_calls.admin_delete_job(job_id=job_id, access_token=current_user.id)

    # Print the status code for debugging purposes
    print(result.status_code)

    if result.status_code == 200:
        flash('Post deleted successfully', category='info')
        return redirect(url_for('admin/admin_all_jobs.html'))
    else:
        abort(result.status_code)


@app.route("/user/delete-job/<job_id>", methods=['GET', 'POST'])
@requires_any_permission("manage_posts")
@login_required
def user_delete_job(job_id):
    result = api_calls.delete_job_opening(job_id=job_id, access_token=current_user.id)
    print(result.status_code)
    if result.status_code == 200:
        return redirect(url_for('user_all_post'))
    else:
        abort(result.status_code)




@app.route('/jobs/add-job', methods=['GET', 'POST'])
@requires_any_permission("manage_posts")
@login_required
def add_post():
    form = forms.AddJobOpening()

    if form.validate_on_submit():
        print('inside form.validate_on_submit')

        if not current_user.company:
            return redirect(url_for('company_register'))

        job_title = form.job_title.data
        target_date = form.target_date.data
        opening_date = form.opening_date.data
        job_type = form.job_type.data
        work_experience = form.work_experience.data
        industry = form.industry.data
        salary = form.salary.data
        address_city = form.address_city.data
        address_country = form.address_country.data
        address_province = form.address_province.data
        address_postal_code = form.address_postal_code.data
        job_description = form.job_description.data
        job_requirements = form.job_requirements.data
        job_benefits = form.job_benefits.data
        job_opening_status = 'Acitve'


        print(form.data)
        print(form.publish.data)

        if form.save_draft.data:
            job_details = {
                "job_title": job_title,
                "target_date": str(target_date),
                "opening_date": str(opening_date),
                "job_type": job_type,
                "job_skills": "",
                "work_experience": work_experience,
                "industry": industry,
                "salary": salary,
                "address_city": address_city,
                "address_country": address_country,
                "address_province": address_province,
                "address_postal_code": address_postal_code,
                "job_description": job_description,
                "job_requirements": job_requirements,
                "job_benefits": job_benefits,
                "job_opening_status": job_opening_status,
                "status": 'draft'
            }

            try:
                result = api_calls.create_job_opening(
                    job_detail=job_details,
                    access_token=current_user.id
                )

                if result:
                    return redirect(url_for('user_all_post'))
                else:
                    flash("Failed to create post", "danger")
            except Exception as e:
                flash(f"Error creating post: {e}", "danger")
        elif form.publish.data:
            print('trying to publish job')
            job_details = {
                "job_title": job_title,
                "target_date": str(target_date),
                "opening_date": str(opening_date),
                "job_type": job_type,
                "job_skills": "",
                "work_experience": work_experience,
                "industry": industry,
                "salary": salary,
                "address_city": address_city,
                "address_country": address_country,
                "address_province": address_province,
                "address_postal_code": address_postal_code,
                "job_description": job_description,
                "job_requirements": job_requirements,
                "job_benefits": job_benefits,
                "job_opening_status": job_opening_status,
                "status": 'published'
            }
            try:
                result = api_calls.create_job_opening(
                    job_detail=job_details,
                    access_token=current_user.id
                )

                if result:
                    flash("Post created successfully", "success")
                    # try:
                    #     print("trying to send mail")
                    #     dateiso = result["created_at"]
                    #     post_slug = result["slug"]
                    #     date = dateiso.split('T')[0]
                    #     print(date)
                    #     post_url = f'{constants.MY_ROOT_URL}/{current_user.username}/posts/{date}/{post_slug}'
                    #     print(post_url)
                    #     send_mails = api_calls.send_newsletter(access_token=current_user.id, subject=form.title.data, body=form.content.data, post_url=post_url)
                    #     print('done')
                    # except Exception as e:
                    #     raise 'Problem sending newsletter' + e
                    # if current_user.role == 'user':
                    #     return redirect(url_for('user_all_post'))
                    # else:
                    #     return redirect(url_for('all_post'))
                    return redirect(url_for('user_all_post'))

                else:
                    flash("Failed to create post", "danger")
            except Exception as e:
                flash(f"Error creating post: {e}", "danger")
    else:
        print(form.errors)

    root_url = constants.ROOT_URL + '/'
    # media_result = api_calls.get_user_all_medias(access_token=current_user.id)
    # if media_result is None:
    media_result = []  # Set result to an empty list

    # forms_result = api_calls.get_user_all_forms(access_token=current_user.id)
    # if forms_result is None:
    forms_result = []  # Set result to an empty list

    if current_user.role == 'user':
        is_service_allowed = api_calls.is_service_access_allowed(current_user.id)
        if is_service_allowed:
            return render_template('add_post.html', form=form, forms_result=forms_result,result=media_result, root_url=root_url)
        return redirect(url_for('user_view_plan'))
    else:
        return render_template('add_post.html', form=form, result=media_result, forms_result=forms_result, root_url=root_url)


@app.route('/generate-ai-content', methods=['POST'])
def generate_ai_content():
    functions = [
        {
            "name": "generate_job_posting",
            "description": "Generate a structured job posting",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_description": {"type": "string", "description": "Detailed job description"},
                    "job_requirements": {"type": "string", "description": "List of job requirements"},
                    "job_benefits": {"type": "string", "description": "List of job benefits"}
                },
                "required": ["job_description", "job_requirements", "job_benefits"]
            }
        }
    ]

    data = request.json
    field = data.get('field', '')
    job_details = data.get('prompt', {})

    # Strict instruction to return clean JSON
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful AI that generates structured job postings."},
            {"role": "user", "content": f"Generate a job posting for: {json.dumps(job_details, indent=2)}"}
        ],
        functions=functions,
        function_call={"name": "generate_job_posting"},  # Force function calling
        temperature=0.7,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    # print(completion)

    # bot_response = completion.choices[0].message.content.strip()
    # print("Bot Response:", bot_response)  # Debugging

    try:
        # Ensure valid JSON response
        response_data = completion.choices[0].message.function_call.arguments
        print(response_data)
        structured_response = json.loads(response_data)
        print("Structured Response:", structured_response)  # Debugging
        return jsonify(success=True, content=structured_response)
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", str(e))  # Debugging
        return jsonify(success=False, error="Failed to parse AI response as JSON", raw_response=bot_response)

    return jsonify(success=False, error="Invalid request")


@app.route('/posts/preview-post', methods=['GET', 'POST'])
@requires_any_permission("manage_posts")
@login_required
def preview_post():
    date_obj = datetime.utcnow()
    formatted_date = date_obj.strftime('%d %B %Y')
    form = forms.AddPost()
    post_preview_json = request.form.get('postPreview', '{}')
    print(f"post_preview_json: {post_preview_json}")  # Debugging line
    post_preview = json.loads(post_preview_json)
    print(f"post_preview: {post_preview}")

    # post_preview = session.get('post_preview', {})
    if request.method == 'GET':
        # Populate the form with the data from the query parameters
        # form.title.data = request.args.get('title')
        # form.content.data = request.args.get('content')
        # form.category.data = request.args.get('category')
        # form.subcategory.data = request.args.get('subcategory')
        # form.tags.data = request.args.get('tags')
        tags_list = post_preview.get('tags', '').split(",")




    if request.method == 'POST':
        tags_list = form.tags.data.split(",")
        if form.save_draft.data:
            try:
                result = api_calls.create_post(
                    title=form.title.data,
                    content=form.content.data,
                    category_id=form.category.data,
                    subcategory_id=form.subcategory.data,
                    tags=tags_list,
                    status='draft',
                    access_token=current_user.id
                )

                if result:

                    if current_user.role == 'user':
                        return redirect(url_for('user_all_post'))
                    else:
                        return redirect(url_for('all_post'))
                else:
                    flash("Failed to create post", "danger")
            except Exception as e:
                flash(f"Error creating post: {e}", "danger")
        elif form.publish.data:
            try:
                result = api_calls.create_post(
                    title=form.title.data,
                    content=form.content.data,
                    category_id=form.category.data,
                    subcategory_id=form.subcategory.data,
                    tags=tags_list,
                    status='published',
                    access_token=current_user.id
                )

                if result:
                    session.pop('post_preview', None)
                    flash("Post created successfully", "success")
                    try:
                        dateiso = result["created_at"]
                        post_slug = result["slug"]
                        date = dateiso.split('T')[0]
                        post_url = f'{constants.MY_ROOT_URL}/{current_user.username}/posts/{date}/{post_slug}'
                        send_mails = api_calls.send_newsletter(access_token=current_user.id, subject=form.title.data,
                                                               body=form.content.data, post_url=post_url)
                    except Exception as e:
                        raise 'Problem sending newsletter' + e
                    if current_user.role == 'user':
                        return redirect(url_for('user_all_post'))
                    else:
                        return redirect(url_for('all_post'))
                else:
                    flash("Failed to create post", "danger")
            except Exception as e:
                flash(f"Error creating post: {e}", "danger")

    return render_template('preview_post.html', post_preview=post_preview, author_name=current_user.username, form=form, tags=tags_list, created_at=formatted_date)

# @app.route("/posts/preview_post", methods=['GET', 'POST'])
# @login_required
# def preview_post():
#     form = forms.AddPost()
#     if request.method == 'POST':
#         # Get form data from request.form since the form is submitted via POST
#         title = request.form.get('title')
#         content = request.form.get('content')
#         category = request.form.get('category')
#         subcategory = request.form.get('subcategory')
#         tag = request.form.getlist('tags')
#
#         # Populate the form with the data
#         form.title.data = title
#         form.content.data = content
#         form.category.data = category
#         form.subcategory.data = subcategory
#         form.tags.data = tag
#
#         # Render the preview page with the populated form
#         return render_template('preview_post.html', title=title, content=content, author_name=current_user.username,
#                                form=form, category=category, subcategory=subcategory, tag=tag)
#
#     return redirect(url_for('add_post'))


# @app.route("/user/add-category", methods=['GET', 'POST'])
# @requires_any_permission("manage_posts")
# @login_required
# def add_category():
#     form = forms.AddCategory()
#     if form.validate_on_submit():
#         category = form.category.data
#         response = api_calls.add_category(category, access_token=current_user.id)
#         print(response.status_code)
#         if (response.status_code == 200):
#             flash('Category added Successful', category='info')
#             return redirect(url_for('user_all_category'))
#         else:
#             flash('Some problem occured', category='error')
#
#     return render_template('user_add_category.html', form=form)
#
# @app.route("/user/update-category/<category_id>", methods=['GET', 'POST'])
# @requires_any_permission("manage_posts")
# @login_required
# def update_category(category_id):
#     form = forms.AddCategory()
#     if form.validate_on_submit():
#         category = form.category.data
#         response = api_calls.update_category(category_id, category, access_token=current_user.id)
#         print(response.status_code)
#         if (response.status_code == 200):
#             flash('Category updated Successful', category='info')
#             return redirect(url_for('user_all_category'))
#         else:
#             flash('Some problem occured', category='error')
#
#     return render_template('update_user_category.html', form=form, category_id=category_id)
#
# @app.route('/user/all-categories')
# @requires_any_permission("manage_posts")
# @login_required
# def user_all_category():
#     result = api_calls.get_user_all_categories(access_token=current_user.id)
#     if result is None:
#         result = []  # Set result to an empty list
#     print(result)
#
#     return render_template('view_user_category.html', result=result)
#
#
# @app.route('/user/all-subcategories/<category_id>')
# @requires_any_permission("manage_posts")
# @login_required
# def user_all_subcategory(category_id):
#     result = api_calls.get_subcategories_by_category(category_id=category_id)
#     if result is None:
#         result = []  # Set result to an empty list
#     print(result)
#
#     return render_template('view_user_subcategory.html', result=result)
#
#
# @app.route("/user/add-tag", methods=['GET', 'POST'])
# @requires_any_permission("manage_posts")
# @login_required
# def add_tag():
#     form = forms.AddTag()
#     if form.validate_on_submit():
#         tag = form.tag.data
#         response = api_calls.add_tag(tag, access_token=current_user.id)
#         print(response.status_code)
#         if (response.status_code == 200):
#             flash('Tag added Successful')
#             return redirect(url_for('user_all_tag'))
#         else:
#             flash('Some problem occured')
#
#     return render_template('user_add_tags.html', form=form)
#
#
# @app.route("/user/edit-tag/<int:tag_id>", methods=['GET', 'POST'])
# @requires_any_permission("manage_posts")
# @login_required
# def edit_tag(tag_id):
#     form = forms.EditTag()
#     if form.validate_on_submit():
#         new_tag = form.tag.data
#         response = api_calls.edit_tag(tag_id, new_tag, access_token=current_user.id)
#         print(response.status_code)
#         if response.status_code == 200:
#             flash('Tag edited successfully')
#             return redirect(url_for('user_all_tag'))
#         else:
#             flash('Some problem occurred while editing the tag')
#
#     return render_template('user_edit_tag.html', form=form, tag_id=tag_id)
#
#
# @app.route("/user/delete-tag/<int:tag_id>", methods=['GET', 'POST'])
# @requires_any_permission("manage_posts")
# @login_required
# def delete_tag(tag_id):
#     response = api_calls.delete_tag(tag_id, access_token=current_user.id)
#     print(response.status_code)
#     if response.status_code == 200:
#         flash('Tag deleted successfully')
#     else:
#         flash('Some problem occurred while deleting the tag')
#     return redirect(url_for('user_all_tag'))
#
#
# @app.route('/user/all-tags')
# @requires_any_permission("manage_posts")
# @login_required
# def user_all_tag():
#     result = api_calls.get_user_all_tags(access_token=current_user.id)
#     if result is None:
#         result = []  # Set result to an empty list
#     print(result)
#
#     return render_template('view_user_tags.html', result=result)
#
#
# @app.route("/users/delete-category/<category_id>", methods=['GET', 'POST'])
# @requires_any_permission("manage_posts")
# @login_required
# def user_delete_category(category_id):
#     result = api_calls.user_delete_category(category_id=category_id, access_token=current_user.id)
#     print(result.status_code)
#     if result.status_code == 200:
#         return redirect(url_for('user_all_category'))
#
#
# @app.route('/user/subcategories/<int:category_id>')
# def get_subcategories(category_id):
#     # Fetch subcategories based on the category_id
#     subcategories = api_calls.get_subcategories_by_category(category_id)
#     return jsonify({'subcategories': subcategories})
#
#
# @app.route("/user/add-subcategory", methods=['GET', 'POST'])
# @requires_any_permission("manage_posts")
# @login_required
# def add_subcategory():
#     form = forms.AddSubcategory()
#     categories = api_calls.get_user_all_categories(access_token=current_user.id)
#     category_choices = [(category['id'], category['category']) for category in categories]
#     form.category.choices = category_choices
#     if form.validate_on_submit():
#         subcategory = form.subcategory.data
#         category_id = form.category.data
#         response = api_calls.add_subcategory(subcategory, category_id, access_token=current_user.id)
#         print(response.status_code)
#         if (response.status_code == 200):
#             flash('Subcategory added Successful', category='info')
#             return redirect(url_for('user_all_category'))
#         else:
#             flash('Some problem occured', category='error')
#
#     return render_template('user_add_subcategory.html', form=form, categories=category_choices)
#
#
# @app.route("/user/update-subcategory/<subcategory_id>", methods=['GET', 'POST'])
# @requires_any_permission("manage_posts")
# @login_required
# def update_subcategory(subcategory_id):
#     form = forms.AddSubcategory()  # Assuming you have a form for subcategory
#     categories = api_calls.get_user_all_categories(access_token=current_user.id)
#     category_choices = [(category['id'], category['category']) for category in categories]
#     form.category.choices = category_choices
#     if form.validate_on_submit():
#         subcategory = form.subcategory.data
#         category_id = form.category.data
#         response = api_calls.update_subcategory(subcategory_id, subcategory, category_id, access_token=current_user.id)
#         print(response.status_code)
#         if (response.status_code == 200):
#             flash('Subcategory added Successful', category='info')
#             return redirect(url_for('user_all_category'))
#         else:
#             flash('Some problem occured', category='error')
#
#     return render_template('update_user_subcategory.html', form=form, subcategory_id=subcategory_id,
#                            categories=category_choices)
#
#
# @app.route("/users/delete-subcategory/<subcategory_id>", methods=['GET', 'POST'])
# @requires_any_permission("manage_posts")
# @login_required
# def user_delete_subcategory(subcategory_id):
#     result = api_calls.user_delete_subcategory(subcategory_id=subcategory_id, access_token=current_user.id)
#     print(result.status_code)
#     if result.status_code == 200:
#         return redirect(url_for('user_all_category'))
#

@app.route('/job-openings/<job_id>', methods=['GET', 'POST'])
@requires_any_permission("manage_posts")
def admin_edit_post(job_id):
    job_opening = api_calls.get_job(job_id=job_id)
    date_format = '%Y-%m-%dT%H:%M:%S%z'

    if 'target_date' in job_opening:
        # Parse the target_date string with the adjusted format
        job_opening['target_date'] = datetime.strptime(job_opening['target_date'], date_format)

    if 'opening_date' in job_opening:
        # Parse the opening_date string with the adjusted format
        job_opening['opening_date'] = datetime.strptime(job_opening['opening_date'], date_format)

    form = forms.AddJobOpening(data=job_opening)

    if form.validate_on_submit():

        job_title = form.job_title.data
        target_date = form.target_date.data
        opening_date = form.opening_date.data
        job_type = form.job_type.data
        work_experience = form.work_experience.data
        industry = form.industry.data
        salary = form.salary.data
        address_city = form.address_city.data
        address_country = form.address_country.data
        address_province = form.address_province.data
        address_postal_code = form.address_postal_code.data
        job_description = form.job_description.data
        job_requirements = form.job_requirements.data
        job_benefits = form.job_benefits.data
        job_opening_status = form.job_opening_status.data

        if form.publish.data:
            print(f"Job Title: {job_title}")
            print(f"Target Date: {target_date}")
            print(f"Opening Date: {opening_date}")
            print(f"Job Type: {job_type}")
            print(f"Work Experience: {work_experience}")
            print(f"Industry: {industry}")
            print(f"Salary: {salary}")
            print(f"City: {address_city}")
            print(f"Country: {address_country}")
            print(f"Province: {address_province}")
            print(f"Postal Code: {address_postal_code}")
            print(f"Job Description: {job_description}")
            print(f"Job Requirements: {job_requirements}")
            print(f"Job Benefits: {job_benefits}")
            print(f"Job Opening Status: {job_opening_status}")

            try:
                job_details=  {
                    "job_title": job_title,
                    "target_date": str(target_date),
                    "opening_date": str(opening_date),
                    "job_type": job_type,
                    "job_skills": "",
                    "work_experience": work_experience,
                    "industry": industry,
                    "salary": salary,
                    "address_city": address_city,
                    "address_country": address_country,
                    "address_province": address_province,
                    "address_postal_code": address_postal_code,
                    "job_description": job_description,
                    "job_requirements": job_requirements,
                    "job_benefits": job_benefits,
                    "job_opening_status": job_opening_status,
                    "status": 'published'
                }

                result = api_calls.update_job(
                    job_id=job_id,
                    job_details=job_details,
                    access_token=current_user.id
                )
                print("redirecting")
                return redirect(url_for('user_all_post'))

                # if result:
                #     print("success")
                #     try:
                #         dateiso = result["created_at"]
                #         post_slug = result["slug"]
                #         date = dateiso.split('T')[0]
                #         post_url = f'{constants.MY_ROOT_URL}/{current_user.username}/posts/{date}/{post_slug}'
                #         print(post_url)
                #         send_mails = api_calls.send_newsletter(access_token=current_user.id, subject=form.title.data,
                #                                                body=form.content.data, post_url=post_url)
                #     except Exception as e:
                #         raise 'Problem sending newsletter' + e
                #     print("Post updated successfully")
                #     if current_user.role == 'user':
                #         print("redirecting")
                #         return redirect(url_for('user_all_post'))
                #     else:
                #         return redirect(url_for('all_post'))
                # else:
                #     print("Failed to update post")
            except Exception as e:
                print(f"Error updating post: {e}")
        elif form.preview.data:
            return redirect(url_for('preview_post',
            job_title=form.job_title.data,
            target_date = form.target_date.data,
            opening_date = form.opening_date.data,
            job_type = form.job_type.data,
            work_experience = form.work_experience.data,
            industry = form.industry.data,
            salary = form.salary.data,
            address_city = form.address_city.data,
            address_country = form.address_country.data,
            address_province = form.address_province.data,
            address_postal_code = form.address_postal_code.data,
            job_description = form.job_description.data,
            job_requirements = form.job_requirements.data,
            job_benefits = form.job_benefits.data,
            job_opening_status = form.job_opening_status.data
            ))

    else:
        print('Not Working')
        print(form.errors)

    return render_template('edit_post_form.html', form=form, job_id=job_id)


############################################################ SUBSCRIPTION #############################################################
@app.route('/payment/<plan_id>', methods=['GET', 'POST'])
@login_required
def payment(plan_id):
    plan = api_calls.get_plan_by_id(plan_id)  # Fetch the plan details from the database or API
    print(plan)

    if plan.get('price') == 0:
        return redirect(url_for('create_subscription', plan_id=plan.id))

    return render_template('payment.html', plan_id=plan_id)


@app.route('/create-subscription/<plan_id>', methods=['GET', 'POST'])
@login_required
def create_subscription(plan_id):
    plan = api_calls.get_plan_by_id(plan_id)  # Fetch the plan details from the database or API
    print(plan)

    if plan.get('price') == 0:
        # Directly create the subscription for free plans
        result = api_calls.start_subscription(plan_id=plan_id, stripe_token=None, access_token=current_user.id)
        if result:
            return redirect(url_for('company_register'))  # Redirect to the user dashboard
        else:
            return redirect(url_for('user_view_plan'))
    else:
        # Handle paid subscriptions
        stripe_token = request.form.get('stripeToken')
        result = api_calls.start_subscription(plan_id=plan_id, stripe_token=stripe_token, access_token=current_user.id)
        if result:
            return render_template('payment_success.html')
        else:
            return render_template('payment_failure.html')


@app.route('/cancel-subscription/<subscription_id>', methods=['GET', 'POST'])
@login_required
def cancel_subscription(subscription_id):
    try:
        result = api_calls.cancel_subscription(subscription_id=subscription_id)
        if result:
            return redirect(url_for('profile'))

    except Exception as e:
        print(e)


@app.route('/resume-subscription/<subscription_id>', methods=['GET', 'POST'])
@login_required
def resume_subscription(subscription_id):
    try:
        result = api_calls.resume_subscription(subscription_id=subscription_id)
        if result:
            return redirect(url_for('profile'))

    except Exception as e:
        print(e)


@app.route('/purchase_history', methods=['GET'])
@login_required
def get_purchase_history():
    access_token = current_user.id
    purchase_data = api_calls.purchase_history(access_token)

    return render_template('purchase_history.html', purchase_data=purchase_data)


@app.route('/admin/all-subscriptions', methods=['GET'])
@login_required
def get_all_subscriptions():
    access_token = current_user.id
    purchase_data = api_calls.get_all_subscriptions(access_token)

    return render_template('all_subscription.html', purchase_data=purchase_data)

    return render_template('all_posts.html', result=result)

########################################## MEDIA #####################################################


@app.route('/jobseeker/upload-resume', methods=['GET', 'POST'])
@login_required
@requires_any_permission("applicants")
def media():
    form = forms.AddMediaForm()  # Use the AddMediaForm class
    if request.method == 'POST':
        files = request.files.getlist('files')
        print(files)
        file_list = []
        file_path_list = []

        # Ensure the media directory exists
        media_folder = 'media'
        if not os.path.exists(media_folder):
            os.makedirs(media_folder)

        for file in files:
            # Ensure the file has a secure filename
            filename = secure_filename(file.filename)
            # Save the file to the designated folder
            file_url = os.path.join(media_folder, filename)
            print(file_url)
            file.save(file_url)
            file_path_list.append(file_url)
            file_list.append(('files', (filename, open(file_url, 'rb'))))

        access_token = current_user.id  # Replace with the actual method to get the access token
        parsed_resumes = parse_multiple_resumes(file_path_list)
        profile_data = {
            'education': parsed_resumes[0].get('Education', []),
            'experience': parsed_resumes[0].get('Experience', []),
            'internships': parsed_resumes[0].get('Internship', []),
            'projects': parsed_resumes[0].get('Projects', []),
            'profile_summary': {'content': parsed_resumes[0].get('ProfileSummary')},
            'skills': parsed_resumes[0].get('Skills', []),
            'accomplishments': parsed_resumes[0].get('Accomplishment', [])
        }
        update_profile = api_calls.update_jobseeker_profile(profile_data=profile_data, access_token=current_user.id)


        # Handle file uploads using a helper function (assuming api_calls.upload_medias is properly defined)
        response = api_calls.upload_medias(file_list, access_token)

        if response and response.status_code == 200:
            empty_folder(media_folder)
            return jsonify({"message": "Media added successfully", "redirect": url_for('jobseeker_profile')}), 200
        else:
            return jsonify({"message": "Some problem occurred"}), response.status_code if response else 500

    return render_template('media.html', form=form)
#
#
@app.route('/jobseeker/my-resume')
@requires_any_permission("applicants")
@login_required
def user_all_medias():
    root_url = constants.ROOT_URL + '/'
    result = api_calls.get_user_all_medias(access_token=current_user.id)
    if result is None:
        result = []  # Set result to an empty list
    print(result)

    return render_template('user_all_media.html', result=result, root_url=root_url)


@app.route("/jobseeker/delete_resume/<media_id>", methods=['GET', 'POST'])
@login_required
def delete_media(media_id):
    result = api_calls.jobseeker_delete_media(media_id=media_id, access_token=current_user.id)
    return redirect(url_for('jobseeker_profile'))




#########################################################3 COMMENTS ##########################################################################

# @app.route('/posts/comment/<int:post_id>/<username>/<post_date>/<post_slug>', methods=['GET', 'POST'])
# @login_required
# def comment(post_id, username, post_date, post_slug):
#     if request.method == 'POST':
#         comment = request.form.get('comment')
#         reply_id = request.form.get('reply_id') if request.form.get('reply_id') else None
#         if comment:
#             try:
#                 response = api_calls.add_comment(
#                     post_id=post_id,
#                     reply_id=reply_id,
#                     comment=comment,
#                     access_token=current_user.id
#                 )
#                 if response.status_code == 200:
#                     return redirect(url_for('get_post_by_username_and_slug', username=username, post_date=post_date, post_slug=post_slug))
#                 else:
#                     flash('An error occurred while adding the comment. Please try again.', category='error')
#             except Exception as e:
#                 flash(f'An exception occurred: {str(e)}', category='error')
#         else:
#             flash('Comment cannot be empty', category='error')
#
#     return redirect(url_for('get_post_by_username_and_slug', username=username, post_date=post_date, post_slug=post_slug))
#
#
# @app.route("/user/delete-comment/<comment_id>", methods=['GET', 'POST'])
# @login_required
# def delete_comment(comment_id):
#     result = api_calls.delete_comment(comment_id=comment_id, access_token=current_user.id)
#     print(result.status_code)
#     if result.status_code == 200:
#         return redirect(url_for('get_all_comment'))
#
#
# @app.route('/posts/all-comment', methods=['GET', 'POST'])
# @login_required
# def get_all_comment():
#     result = api_calls.get_all_comments(access_token = current_user.id)
#     if result is None:
#         result = []  # Set result to an empty list
#     print(result)
#
#     return render_template('comments_table.html', result=result)
#
#
# @app.route('/posts/activate-comment/<comment_id>', methods=['GET', 'POST'])
# @login_required
# def activate_comment(comment_id):
#     response = api_calls.activate_comments(comment_id=comment_id)
#     if response:
#         return redirect(url_for('get_all_comment'))
#
#
# @app.route('/posts/deactivate-comment/<comment_id>', methods=['GET', 'POST'])
# @login_required
# def deactivate_comment(comment_id):
#     response = api_calls.deactivate_comments(comment_id=comment_id)
#     if response:
#         return redirect(url_for('get_all_comment'))
#
#
# @app.route('/settings/comments', methods=['GET', 'POST'])
# @login_required
# def comment_setting():
#     print("comment setting")
#     if request.method == 'POST':
#         # Extract form data
#         def get_bool_value(value):
#             return value == 'on'
#         print("chal rah hai")
#         def get_int_value(value, default):
#             try:
#                 return int(value)
#             except (ValueError, TypeError):
#                 return default
#
#         settings = {
#             'notify_linked_blogs': get_bool_value(request.form.get('notify_linked_blogs')),
#             'allow_trackbacks': get_bool_value(request.form.get('allow_trackbacks')),
#             'allow_comments': get_bool_value(request.form.get('allow_comments')),
#             'comment_author_info': get_bool_value(request.form.get('comment_author_info')),
#             'registered_users_comment': get_bool_value(request.form.get('registered_users_comment')),
#             'auto_close_comments': get_int_value(request.form.get('auto_close_comments'), 14),
#             'show_comment_cookies': get_bool_value(request.form.get('show_comment_cookies')),
#             'enable_threaded_comments': get_bool_value(request.form.get('enable_threaded_comments')),
#             'email_new_comment': get_bool_value(request.form.get('email_new_comment')),
#             'email_held_moderation': get_bool_value(request.form.get('email_held_moderation')),
#             'email_new_subscription': get_bool_value(request.form.get('email_new_subscription')),
#             'comment_approval': request.form.get('comment_approval')
#         }
#
#         try:
#             # Call an API endpoint to save the settings
#             response = api_calls.save_comment_settings(
#                 access_token=current_user.id,
#                 settings=settings
#             )
#
#             if response.status_code == 200:
#                 flash('Settings saved successfully', category='success')
#             else:
#                 flash('An error occurred while saving settings. Please try again.', category='error')
#         except Exception as e:
#             flash(f'An exception occurred: {str(e)}', category='error')
#
#     result = api_calls.get_comments_settings(
#         access_token=current_user.id
#     )
#
#     return render_template('comments_settings.html', result=result)
#
#
#
# @app.route('/comments/like/<int:post_id>/<int:comment_id>/<username>/<post_date>/<post_slug>')
# @login_required
# def add_like_to_comment_route(post_id, comment_id, username, post_date, post_slug):
#     print("ander hu")
#     try:
#         # Example: Get access_token from current_user or session
#         access_token = current_user.id
#
#         # Call the api_calls method to add like to comment
#         response = api_calls.add_like_to_comment(post_id, comment_id, access_token)
#
#
#         if response and response.status_code == 200:
#             flash('Like added successfully', category='info')
#             return redirect(url_for('get_post_by_username_and_slug', username=username, post_date=post_date, post_slug=post_slug))
#             print("hii")
#         else:
#             flash('Failed to add like', category='error')
#     except Exception as e:
#         flash(f'Error: {str(e)}', category='error')
#
#     return redirect(url_for('get_post_by_username_and_slug', username=username, post_date=post_date, post_slug=post_slug))
#
#
# @app.route('/comments/remove-like/<int:comment_like_id>/<int:comment_id>/<username>/<post_date>/<post_slug>')
# @login_required
# def remove_like_from_comment_route(comment_like_id, comment_id, username, post_date, post_slug):
#     print("ander hu")
#     try:
#         # Example: Get access_token from current_user or session
#         access_token = current_user.id
#
#         # Call the api_calls method to add like to comment
#         response = api_calls.remove_like_from_comment(comment_like_id, access_token)
#
#
#         if response and response.status_code == 200:
#             flash('Like removed successfully', category='info')
#             return redirect(url_for('get_post_by_username_and_slug', username=username, post_date=post_date, post_slug=post_slug))
#             print("hii")
#         else:
#             flash('Failed to remove like', category='error')
#     except Exception as e:
#         flash(f'Error: {str(e)}', category='error')
#
#     return redirect(url_for('get_post_by_username_and_slug', username=username, post_date=post_date, post_slug=post_slug))
#
# @app.route('/users/view-posts')
# def view_post():
#     result = api_calls.get_all_posts()
#     response = api_calls.get_all_categories()
#     if result is None:
#         result = []  # Set result to an empty list
#
#     if response is None:
#         response = []
#     print(result)
#
#     return render_template('list_of_posts.html', result=result, response=response)
#
#
# @app.route('/posts/<post_title>', methods=['GET', 'POST'])
# def get_post(post_title):
#     if request.method == 'POST':
#         post_id = request.form.get('post_id')
#         session['post_id'] = post_id  # Store post_id in session
#     else:
#         post_id = session.get('post_id')  # Retrieve post_id from session
#
#     response = api_calls.get_post(post_id=post_id)
#     category_name = response["category_name"]
#     content = response["content"]
#     author_name = response["author_name"]
#     created_at = response["created_at"]
#     date_obj = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%S.%f%z')
#     formatted_date = date_obj.strftime('%d %B %Y')
#     tags = response["tags"]
#
#     result = api_calls.get_a_post_all_comments(post_id=post_id)
#     if result is None:
#         result = []  # Set result to an empty list
#
#
#
#     return render_template('post.html', title=post_title, content=content, author_name=author_name,
#                            created_at=formatted_date, category=category_name, tags=tags, result=result, post_id=post_id)
#


# @app.route('/<username>/jobs/<job_date>/<job_slug>', methods=['GET', 'POST'])
# def get_post_by_username_and_slug(username, job_date, job_slug):
#     job_details = api_calls.get_job_by_username_slug(job_ownername=username, slug=job_slug)
#     apply_form = forms.ApplyToJob()
#     apply_form.job_id.data = job_details["id"]
#     if apply_form.validate_on_submit:
#         if apply_form.resume.data:
#             applied = api_calls.apply_to_job_via_resume_list(access_token=current_user.id, resume_id=apply_form.resume.data, job_id=apply_form.job_id.data)
#             return redirect(url_for('get_post_by_username_and_slug', username=username, job_date=job_date, job_slug=job_slug))
#
#         elif apply_form.upload_resume.data:
#             empty_folder(uploads_folder)
#             file = apply_form.upload_resume.data
#
#             filename = secure_filename(file.filename)
#             # Save the file to a designated folder
#             file_path = 'uploads/' + filename
#             print(file_path)
#             file.save(file_path)
#             payload = {'resume_file': (filename, open(file_path, 'rb'))}
#
#             api_calls.apply_to_job_via_device(access_token=current_user.id, file=payload,
#                                                    job_id=apply_form.job_id.data)
#             return redirect(url_for('get_post_by_username_and_slug', username=username, job_date=job_date, job_slug=job_slug))
#
#     return render_template('post.html',job_details=job_details, job_id=id, job_date=job_date, job_slug=job_slug, form=apply_form)


@app.route('/jobs/<job_date>/<job_slug>', subdomain='<company_subdomain>', methods=['GET', 'POST'])
def get_post_by_company_subdomain_and_slug(company_subdomain, job_date, job_slug):
    access_token = current_user.id if current_user.is_authenticated else None

    job_details = api_calls.get_job_by_company_subdomain_slug(
        company_subdomain=company_subdomain,
        slug=job_slug,
        access_token=access_token
    )
    apply_form = forms.ApplyToJob()
    apply_form.job_id.data = job_details["id"]
    print(job_details.get('applied'))
    print(job_details.get('company_logo'))
    if request.method == 'POST':
        applied = api_calls.apply_to_job_via_resume_list(access_token=current_user.id, job_id=apply_form.job_id.data)
        if applied:  # Assuming API call returns success status
            flash('Job application submitted successfully!', 'success')
        else:
            flash('Failed to apply for the job. Please try again.', 'error')
        return redirect(url_for('get_post_by_company_subdomain_and_slug', company_subdomain=company_subdomain, job_date=job_date, job_slug=job_slug))

    return render_template('post.html',job_details=job_details, job_id=id, job_date=job_date, job_slug=job_slug, form=apply_form)


###################################form builder################

@app.route('/formbuilder')
@requires_any_permission("manage_forms")
@login_required
def formbuilder():
    unique_id = str(uuid.uuid4())
    return render_template('cms/formbuilder/formbuilder.html', form_unique_id=unique_id)


@app.route('/formbuilder/form-create', methods=['GET', 'POST'])
@requires_any_permission("manage_forms")
@login_required
def formbuilder_createform():
    data = request.get_json()
    print('IN FORM CREATE')
    print(data)
    form_name = data.get('form_name', '')
    form_html = data.get('form_html', '')
    unique_id = data.get('unique_id', '')
    try:
        form_created = api_calls.create_form(form_name=form_name, form_html=form_html, form_unique_id=unique_id, access_token=current_user.id)
        return redirect(url_for('user_all_forms'))
    except Exception as e:
        print(e)
        return redirect(url_for('formbuilder'))

@app.route("/form/delete-form/<form_id>", methods=['GET', 'POST'])
@requires_any_permission("manage_forms")
@login_required
def formbuilder_delete_form(form_id):
    result = api_calls.delete_form_by_unique_id(form_id=form_id, access_token=current_user.id)
    return redirect(url_for('user_all_forms'))

@app.route('/user/all-forms')
@requires_any_permission("manage_forms")
@login_required
def user_all_forms():
    forms = api_calls.get_user_all_forms(access_token=current_user.id)
    if forms is None:
        forms = []  # Set result to an empty list


    return render_template('cms/formbuilder/user_all_forms.html', result=forms)


@app.route('/user/forms/<form_id>', methods=['GET', 'POST'])
@requires_any_permission("manage_forms")
@login_required
def formbuilder_viewform(form_id):
    response = api_calls.get_form_by_unique_id(form_id=form_id)
    form_name = response["form_name"]
    form_html = response["form_html"]
    form_responses = response["responses"]


    # Convert the set back to a list since we'll pass it to the template
    if form_responses is None:
        form_responses = []
    else:
        form_responses = [json.loads(item) for item in form_responses]

    return render_template('cms/formbuilder/view_form.html', form_html=form_html,form_name=form_name, form_responses=form_responses)


@app.route('/form/thank-you')
def dynamic_form_submission():
    from urllib.parse import urlparse, parse_qs
    parsed_url = urlparse(str(request.url))
    query_string = parsed_url.query

    # Parse the query string into a dictionary
    query_params = parse_qs(query_string)

    unique_id = query_params.pop('unique_id', [''])[0]

    # Process the query parameters to concatenate values of repeated keys
    query_dict = {}
    for k, v in query_params.items():
        # Join values with spaces if there are multiple occurrences, otherwise just take the first value
        query_dict[k] = ' '.join(v) if len(v) > 1 else v[0]

    print("Unique ID:", unique_id)
    print("Query Dictionary:", query_dict)

    submit_form_response = api_calls.collect_form_response(unique_id=unique_id, response_data=query_dict)

    return render_template('widgets/response_recored_modal.html',show_modal='true')


############################################# Email Templates ################################

@app.route("/email-templates/all", methods=['GET', 'POST'])
@login_required
def list_of_email_templates():
    result = api_calls.get_all_email_templates(access_token=current_user.id)
    return render_template('list_of_email_templates.html', result=result)


@app.route("/email-templates/create-template", methods=['GET', 'POST'])
def create_template():
    form = forms.CreateEmailTemplate()
    print("outside")
    if form.validate_on_submit():
        name = form.name.data
        subject = form.subject.data
        body = form.content.data
        result = api_calls.create_template(name, subject, body, access_token=current_user.id)
        print("inside")
        return redirect(url_for('list_of_email_templates'))

    return render_template('create_email_template.html', form=form)


@app.route("/email-templates/update-template/<template_id>", methods=['GET', 'POST'])
@login_required
def update_email_template(template_id):
    form = forms.UpdateEmailTemplate()
    result = api_calls.get_email_template_by_id(template_id=template_id, access_token=current_user.id)
    name = result["name"]
    subject = result["subject"]
    body = result["body"]

    if form.validate_on_submit():
        # Update user information
        name = form.name.data
        subject = form.subject.data
        body = form.content.data

        result = api_calls.edit_eamil_template(template_id=template_id,
                                               name=name, subject=subject, body=body, access_token=current_user.id)
        return redirect(url_for('list_of_email_templates'))

    # Prefill the form fields with user information
    form.name.data = name
    form.subject.data = subject
    form.content.data = body

    return render_template('update_email_template.html', subject=subject, name=name, form=form, body=body,
                           template_id=template_id)


@app.route("/email-templates/delete-template/<template_id>", methods=['GET', 'POST'])
@login_required
def delete_email_template(template_id):
    result = api_calls.delete_template(template_id=template_id, access_token=current_user.id)
    return redirect(url_for('list_of_email_templates'))


############################## Sending Email #####################################################

@app.route("/email-templates/<template_id>/send-mail", methods=['GET', 'POST'])
@login_required
def send_mails(template_id):
    form = forms.SendEmail()
    result = api_calls.get_email_template_by_id(template_id=template_id, access_token=current_user.id)
    subject = result["subject"]
    body = result["body"]

    if form.validate_on_submit():
        # Update user information
        to = form.to.data
        subject = form.subject.data
        body = form.content.data

        result = api_calls.send_email(to=to, subject=subject, body=body, access_token=current_user.id)
        return redirect(url_for('list_of_email_templates'))

    # Prefill the form fields with user information

    form.subject.data = subject
    form.content.data = body

    return render_template('send_emails.html', subject=subject, form=form, body=body, template_id=template_id)


@app.route("/email-settings", methods=['GET', 'POST'])
@login_required
def email_settings():
    return render_template('user_email_dashboard.html')


############################################################## NEWSLETTER ##############################################################


@app.route("/newsletter-subscribers", methods=['GET', 'POST'])
@login_required
def newsletter_subscribers():
    subscriber_info = api_calls.get_all_newsletter_subscribers(access_token=current_user.id)
    subscribers = subscriber_info['subscribers']
    sub_count = subscriber_info['active_sub_count']
    unsub_count = subscriber_info['inactive_sub_count']

    return render_template('newsletter_subscribers.html', result=subscribers, sub_count=sub_count,
                           unsub_count=unsub_count)


@app.route("/unsubscribe-newsletter/<username>", methods=['GET', 'POST'])
def unsubscribe_newsletter(username):
    form = forms.UnsubscribeToNewsletterForm()
    print('out')
    if form.validate_on_submit():
        print('inside')

        # Update user information
        email = form.email.data
        print(email)
        api_calls.unsubscribe_newsletter(email=email, username=username)
        if result:
            return redirect(url_for('unsubscribe_newsletter', username=username,  success=True))
    else:
        print('Validation failed:', form.errors)
    # Render the template with the modal form
    return render_template('widgets/unsubscribe_modal.html', form=form, username=username)


@app.route("/<username>/pages/contact-form", methods=['GET', 'POST'])
def user_contact_form(username):
    if request.method == 'POST':
        fname = request.form.get('firstName')
        lname = request.form.get('lastName')
        email = request.form.get('email')
        message = request.form.get('message')
        try:
            message_sent = api_calls.user_contact_form(username=username, firstname=fname, lastname=lname, email=email,message=message)
        except Exception as e:
            print(e)
        return redirect(url_for('user_post_list', username=username))


@app.route("/user/feedbacks", methods=['GET', 'POST'])
@login_required
def user_feedbacks():
    feedbacks = api_calls.get_all_user_feedbacks(access_token=current_user.id)

    return render_template('user_feedbacks.html', result=feedbacks)

# @app.route("/<username>/posts/category/<category>/<category_id>", methods=['GET', 'POST'])
# def posts_by_category(username, category, category_id):
#     posts= api_calls.get_post_by_category_id(author_name=username, category_id=category_id)
#     return render_template('post_by_filter.html', result=posts, filter_by=category)
#
#
# @app.route("/<username>/posts/tag/<tag>/<tag_id>", methods=['GET', 'POST'])
# def posts_by_tag(username, tag, tag_id):
#     posts= api_calls.get_post_by_tags(username=username, tag_id=tag_id)
#     return render_template('post_by_filter.html', result=posts, filter_by=tag)


#################################################### PAGES ##################################################


@app.route('/user/pages/add-page', methods=['GET', 'POST'])
@requires_any_permission("manage_pages")
@login_required
def add_page():
    form = forms.AddPage()

    if form.validate_on_submit():
        if form.save_draft.data:
            try:
                result = api_calls.create_page(
                    title=form.title.data,
                    content=form.content.data,
                    status='draft',
                    access_token=current_user.id
                )

                if result:
                    if current_user.role == 'user':
                        return redirect(url_for('user_all_pages'))
                    else:
                        return redirect(url_for('all_post'))
                else:
                    flash("Failed to create post", "danger")
            except Exception as e:
                flash(f"Error creating post: {e}", "danger")
        elif form.publish.data:
            try:
                print(form.errors)
                result = api_calls.create_page(
                    title=form.title.data,
                    content=form.content.data,
                    status='published',
                    access_token=current_user.id
                )

                if result:
                    if current_user.role == 'user':
                        return redirect(url_for('user_all_pages'))
                    else:
                        return redirect(url_for('all_pages'))
                else:
                    flash("Failed to create page", "danger")
            except Exception as e:
                flash(f"Error creating page: {e}", "danger")
    else: print(form.errors)

    root_url = constants.ROOT_URL + '/'
    media_result = api_calls.get_user_all_medias(access_token=current_user.id)
    if media_result is None:
        media_result = []  # Set result to an empty list

    forms_result = api_calls.get_user_all_forms(access_token=current_user.id)
    if forms_result is None:
        forms_result = []  # Set result to an empty list

    if current_user.role == 'user':
        is_service_allowed = api_calls.is_service_access_allowed(current_user.id)
        if is_service_allowed:
            return render_template('cms/pages/add_page.html', form=form,forms_result=forms_result, result=media_result, root_url=root_url)
        return redirect(url_for('user_view_plan'))
    else:
        return render_template('cms/pages/add_page.html', form=form,forms_result=forms_result, result=media_result, root_url=root_url)


@app.route('/user/all-pages')
@requires_any_permission("manage_pages")
@login_required
def user_all_pages():
    pages = api_calls.get_user_all_pages(access_token=current_user.id)
    if pages is None:
        pages = []  # Set result to an empty list

    return render_template('cms/pages/user_all_pages.html', result=pages)


@app.route('/user/page/<page_id>', methods=['GET', 'POST'])
@requires_any_permission("manage_pages")
@login_required
def get_page_by_id(page_id):
    response = api_calls.get_page(page_id=page_id)
    title = response["title"]
    content = response["content"]

    return render_template('cms/pages/page.html', title=title, content=content)


@app.route('/user/pages/update-page/<page_id>', methods=['GET', 'POST'])
@requires_any_permission("manage_pages")
@login_required
def update_page(page_id):
    form = forms.AddPage()
    page = api_calls.get_page(page_id=page_id)


    if form.validate_on_submit():

        title = form.title.data
        content = form.content.data

        if form.publish.data:
            try:
                result = api_calls.update_page(
                    page_id=page_id,
                    title=title,
                    content=content,
                    status='published',
                    access_token=current_user.id
                )
                if current_user.role == 'user':
                    print("redirecting")
                    return redirect(url_for('user_all_pages'))

            except Exception as e:
                print(f"Error updating post: {e}")
        elif form.save_draft.data:
            try:
                result = api_calls.update_page(
                    page_id=page_id,
                    title=title,
                    content=content,
                    status='draft',
                    access_token=current_user.id  
                )
                if current_user.role == 'user':
                    return redirect(url_for('user_all_pages'))
            except Exception as e:
                print(f"Error updating post: {e}")
    form.title.data = page['title']
    form.content.data = page['content']

    return render_template('cms/pages/update_page.html', form=form, page=page)


@app.route("/user/pages/delete-page/<page_id>", methods=['GET', 'POST'])
@requires_any_permission("manage_pages")
@login_required
def user_delete_page(page_id):
    result = api_calls.delete_page(page_id=page_id, access_token=current_user.id)
    if result.status_code == 200:
        return redirect(url_for('user_all_pages'))


@app.route('/<username>/pages/<page_slug>', methods=['GET', 'POST'])
def get_page_by_username_and_slug(username, page_slug):
    response = api_calls.get_page_by_username_slug(page_ownername=username, page_slug=page_slug)
    id = response["id"]
    title = response["title"]
    content = response["content"]
    author_name = response["author_name"]
    created_at = response["created_at"]
    date_obj = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%S.%f%z')
    formatted_date = date_obj.strftime('%d %B %Y')

    return render_template('cms/pages/page.html', title=title, content=content)

#######################################################  AI #########################################################################

###################################################### CHATBOT ####################################################################

@app.route('/chatbot')
# @requires_any_permission("access_chatbot")
# @login_required
def chatbot():
    try:
        all_chats = api_calls.get_user_all_chats(access_token=current_user.id)
    except:
        all_chats = []

    return render_template('cms/AI/chatbot.html', all_chats=all_chats)


@app.route('/send_message', methods=['POST'])
# @requires_any_permission("access_chatbot")
def send_message():

    user_input = request.form['user_input']
    print(user_input)

    # Send the user input to OpenAI's GPT-3.5
    completion = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": user_input,
            },
        ],
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    bot_response = completion.choices[0].message.content
    print(bot_response)

    return jsonify({'bot_response': bot_response})


@app.route('/save-chat', methods=['POST'])
@requires_any_permission("access_chatbot")
@login_required
def save_chat():
    data = request.get_json()
    messages = data.get('messages', [])
    try:
        saved = api_calls.chatbot_save_chat(messages=messages, access_token=current_user.id)
        return 'true'
    except Exception as e:
        print(e)
        return 'false'




################################################## RESUME PARSER ######################################################################

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)  # Updated line
        text = ''
        for page in reader.pages:  # Updated line
            text += page.extract_text()  # Updated line
    return text

def extract_text_from_word(file_path):
    from docx import Document
    doc = Document(file_path)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text

def parse_single_resume(resume_text):
    prompt=f"""
    Extract the following information from this resume in JSON format:
    - Name
    - Address
    - Email
    - Phone
    - Education (institution_name, degree, field_of_study, start_date, end_date, is_ongoing)
    - Experience (position, company_name, responsibilities(String), start_date, end_date, is_ongoing)
    - Project (title, description, project_url)
    - Internship (company_name, position, start_date, end_date, job_description, is_ongoing)
    - Accomplishment (title, description, achievement_date)
    - ProfileSummary (content)
    - Skills (list)
    - IndustryKeywords (list)
    - LeadershipKeywords (list)
    - Score (Score the resume from 0 to 100 based on your asessment)
    
    Note: Please generate a response that does not exceed 4096 tokens to ensure completeness.

    Resume:
    {resume_text}

    Give JSON object
    """
    completion = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_tokens=4096,
        n=1,
        stop=None,
        temperature=0.5,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    json_resume = completion.choices[0].message.content
    print(type(json_resume))
    cleaned_json_string = json_resume.strip('```json ').strip('```')
    data = json.loads(cleaned_json_string)
    print(data)
    # json_string = json_resume.replace('json ', '')
    # print(json_string)
    #
    # try:
    #     parsed_data = clean_json_response(json_resume)
    #
    # except Exception as e:
    #     parsed_data = {"error": str(e)}

    return data

def clean_json_response(response_text):
    import re
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        cleaned_response = re.sub(r'\s+', '', response_text)  # Remove extra whitespace
        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse resume information into JSON"}

def parse_multiple_resumes(file_paths):
    parsed_resumes = []
    for file_path in file_paths:
        if file_path.endswith('.pdf'):
            resume_text = extract_text_from_pdf(file_path)
            print('Extracted PDF')
        elif file_path.endswith('.docx'):
            resume_text = extract_text_from_word(file_path)
            print('Extracted WORD')
        else:
            raise ValueError("Unsupported file type. Use 'pdf' or 'word'.")

        parsed_data = parse_single_resume(resume_text)
        print('GOT JSON')
        parsed_resumes.append(parsed_data)
    return parsed_resumes


@app.route('/resume-parser', methods=['GET', 'POST'])
# @requires_any_permission("access_resume_parser")
@login_required
def resume_parser():
    form = forms.UploadForm()
    if form.validate_on_submit():
        uploaded_files = request.files.getlist('files')

        # Clear the uploads folder
        empty_folder(uploads_folder)

        file_list = []
        for file in uploaded_files:
            filename = secure_filename(file.filename)
            file_path = os.path.join(uploads_folder, filename)
            file.save(file_path)
            file_list.append(file_path)

        parsed_resumes = parse_multiple_resumes(file_list)


        try:
            resume_submission = api_calls.add_new_resume_collection(resumes=parsed_resumes, access_token=current_user.id)

        except Exception as e:
            raise e

        # Render results
        return parsed_resumes

    return render_template('upload_pdf.html', form=form)


@app.route('/resume-collection')
@requires_any_permission("access_resume_parser")
@login_required
def resume_collection():
    try:
        resume_collection = api_calls.get_past_resume_records(access_token=current_user.id)
    except: resume_collection = []

    return render_template('cms/AI/resume_collection.html', result=resume_collection)

#####################################################################################################################################################################################################
##################################################### ADMIN ######################################################################

@app.route('/admin/role-management')
@requires_any_permission("manage_user")
@login_required
def role_management():
    try:
        security_groups = api_calls.get_all_security_groups(access_token=current_user.id)
    except: security_groups = []

    return render_template('admin/all_security_groups.html', result=security_groups)

@app.route('/admin/create-group', methods=['GET', 'POST'])
@requires_any_permission("manage_user")
@login_required
def create_group():
    if request.method == 'POST':
        group_name = request.form['group_name']
        permissions = request.form.getlist('permissions[]')
        # Here you would typically save these details to a database
        submission = api_calls.create_security_group(access_token=current_user.id, permissions=permissions, group_name=group_name)
        print(f"Group Name: {group_name}, Permissions: {permissions}")
        return redirect(url_for('role_management'))

    return render_template('admin/add_security_group.html')


@app.route('/admin/update-group/<int:group_id>', methods=['GET', 'POST'])
@requires_any_permission("manage_user")
@login_required
def update_group(group_id):
    group = api_calls.get_security_group(access_token=current_user.id, group_id=group_id)  # Assume this is fetched from your database

    if request.method == 'POST':
        group_name = request.form['group_name']
        permissions = request.form.getlist('permissions[]')

        print(f"Updating Group ID: {group_id}, Group Name: {group_name}, Permissions: {permissions}")
        updation = api_calls.update_security_group(access_token=current_user.id, permissions=permissions, group_name=group_name, group_id=group_id)
        return redirect(url_for('role_management'))


    return render_template('admin/update_security_group.html', group=group)

@app.route('/admin/delete-group/<group_id>', methods=['GET', 'POST'])
@requires_any_permission("manage_user")
@login_required
def delete_security_group(group_id):
    try:
        deletion = api_calls.delete_security_groups(access_token=current_user.id, group_id=group_id)
        return redirect(url_for('role_management'))
    except:
        return redirect(url_for('role_management'))


########################################### JOBSEEKER MODULE #################################################

@app.route('/jobseeker/dashboard', methods=['GET', 'POST'])
@requires_any_permission("applicants")
@login_required
def jobseeker_dashboard():
    stats = api_calls.get_jobseeker_stats(access_token=current_user.id)

    total_resumes = stats["total_resumes"]
    total_applications = stats["applications_count"]
    profile_completion_percentage = stats["profile_completion_percentage"]
    recommendations = api_calls.get_jobseeker_recommendations(jobs_count=5, access_token=current_user.id)

    return render_template('jobseeker/jobseeker_dashboard.html', total_resumes=total_resumes, total_applications=total_applications, profile_completion_percentage=profile_completion_percentage, recommendations=recommendations)


@app.route('/jobseeker/login', methods=['GET', 'POST'])
def jobseeker_login():
    session.pop('_flashes', None)
    print('trying')
    if current_user.is_authenticated:
        return redirect(url_for('jobseeker_dashboard'))
    form = forms.LoginForm()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        response = api_calls.jobseeker_login(email, password)

        if response is not None and response.status_code == 200:
            data = response.json()
            id = data.get('id')
            token = data.get('access_token')
            role = data.get('role')
            firstname = data.get('firstname')
            lastname = data.get('lastname')
            username = data.get('username')
            email = data.get('email')
            company = {}
            group = data.get('group', {})
            profile_picture = data['profile_picture']

            user = User(id=id, user_id=token, role=role, firstname=firstname, lastname=lastname, username=username, email=email, company=company,
                        group=group, profile_picture=profile_picture)
            login_user(user)
            session['user'] = {
                'id': id,
                'user_id': token,
                'role': role,
                'firstname': firstname,
                'lastname':lastname,
                'username': username,
                'email': email,
                'company': company,
                'group':group,
                'profile_picture': profile_picture,
            }
            return redirect(url_for('jobseeker_dashboard'))
        elif response.status_code == 400:
            result = response.json()
            message = result["detail"]
            flash(message, category='error')
        else:
            # Handle the case where the response is None or the status code is not 200
            print("Error: Response is None or status code is not 200")
            flash('Login unsuccessful. Please check email and password.', category='error')

    return render_template('jobseeker/jobseeker_login.html', form=form)

@app.route("/get-country-codes", methods=["GET"])
def get_country_codes():
    from phonenumbers.phonenumberutil import COUNTRY_CODE_TO_REGION_CODE

    country_list = []
    for code, regions in COUNTRY_CODE_TO_REGION_CODE.items():
        # Skip the special non-geographic code "001"
        if str(code) == "001":
            continue
        for region in regions:
            country_list.append({
                "name": region,
                "dial_code": f"+{code}"
            })

    # Sort countries alphabetically by name
    sorted_countries = sorted(country_list, key=lambda x: x["name"])
    return jsonify(sorted_countries)


@app.route("/validate-phone", methods=["POST"])
def validate_phone():
    import phonenumbers
    data = request.json
    phone = data.get("phone")
    country_code = data.get("country_code")

    if not phone or not country_code:
        return jsonify({"valid": False, "error": "Phone number and country code are required"}), 400

    try:
        parsed_number = phonenumbers.parse(phone, country_code)
        if phonenumbers.is_valid_number(parsed_number):
            return jsonify({"valid": True})
        else:
            return jsonify({"valid": False, "error": "Invalid phone number"}), 400
    except phonenumbers.NumberParseException:
        return jsonify({"valid": False, "error": "Invalid phone number"}), 400


@app.route('/jobseeker/register', methods=['GET', 'POST'])
def jobseeker_register():
    session.pop('_flashes', None)

    form = forms.JobseekerRegisterForm()
    print("outside")
    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = form.lastname.data
        phone_number = form.phone_number.data
        email = form.email.data
        password = form.password.data
        response = api_calls.jobseeker_register(firstname,lastname,phone_number, email, password)
        print("inside")
        if response.status_code == 200:
            response = api_calls.jobseeker_login(email, password)
            if response is not None and response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                id = data.get('id')
                role = data.get('role')
                firstname= data.get('firstname')
                lastname = data.get('lastname')
                username = data.get('username')
                email = data.get('email')
                company = {}
                group = data.get('group', {})
                profile_picture = data['profile_picture']

                user = User(id=id, user_id=token, role=role, username=username, email=email, firstname=firstname, lastname=lastname,
                            company=company, group=group,
                            profile_picture=profile_picture)
                login_user(user)
                session['user'] = {
                    'id': id,
                    'user_id': token,
                    'role': role,
                    'firstname': firstname,
                    'lastname': lastname,
                    'username': username,
                    'email': email,
                    'company': company,
                    'group': group,
                    'profile_picture': profile_picture
                }
            flash('Registration Successful', category='info')
            return redirect(url_for('jobseeker_profile_choice'))
        elif response.status_code == 400:
            result = response.json()
            message = result["detail"]
            flash(message, category='error')

        else:
            flash('Registration unsuccessful. Please check username, email and password.', category='error')

    return render_template('jobseeker/jobseeker_register.html', form=form)


@app.route('/jobseeker/logout')
def jobseeker_logout():
    if current_user:
        logout_user()
        session.clear()
        flash('Logout successful!', 'success')
    return redirect(url_for('jobseeker_login'))


@app.route('/jobseeker/my-applications')
@requires_any_permission("applicants")
@login_required
def jobseeker_applications():
    result = api_calls.get_jobseeker_applications(access_token=current_user.id)
    if result is None:
        result = []  # Set result to an empty list

    return render_template('jobseeker/job_applications.html', result=result)


@app.route('/update-application-status', methods=['GET','POST'])
@requires_any_permission("manage_posts")
@login_required
def update_application_status():
    item_id = request.json['id']
    new_status = request.json['newStatus']
    print(item_id, new_status)

    result = api_calls.update_application_status(application_id=item_id, new_status=new_status)
    return jsonify(result)


@app.route('/setup-applicant-tracking')
@requires_any_permission("manage_posts")
@login_required
def applicant_tracking():
    result = api_calls.get_board_columns(access_token=current_user.id)
    if result is None:
        result = []  # Set result to an empty list

    return render_template('cms/job_openings/applicant_tracking_setup.html', result=result)


@app.route('/setup-applicant-tracking/create', methods=['GET', 'POST'])
@requires_any_permission("manage_posts")
@login_required
def create_applicant_tracker():
    form = forms.AddTrackers()
    print("outside validate on submit")
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        job_status = form.job_status.data
        on_apply = form.on_apply.data
        print("sending request to add plan")
        result = api_calls.create_application_tracker(name=name, description=description, job_status=job_status, on_apply=on_apply, access_token=current_user.id)
        if result:
            return redirect(url_for('applicant_tracking'))
    else:
        print(form.errors)

    return render_template('cms/job_openings/add_applicant_tracker.html', form=form)

@app.route('/setup-applicant-tracking/delete/<id>', methods=['GET', 'POST'])
@requires_any_permission("manage_posts")
@login_required
def delete_applicant_tracker(id):
    result = api_calls.delete_application_tracker(tracker_id=id, access_token=current_user.id)
    if result:
        return redirect(url_for('applicant_tracking'))



@app.route('/jobseeker/profile', methods=['GET', 'POST'])
@requires_any_permission("applicants")
@login_required
def jobseeker_profile():
    root_url = constants.ROOT_URL + '/'
    about_form = forms.AboutForm()
    education_form = forms.EducationForm()
    experience_form = forms.ExperienceForm()
    internship_form = forms.InternshipForm()
    project_form = forms.ProjectForm()
    accomplishment_form = forms.AccomplishmentForm()
    name_form = forms.CollectNameForm()
    email_form  = forms.CollectEmailForm()
    phone_form = forms.CollectPhoneForm()
    profile_picture_form = forms.CollectProfilePictureForm()

    profile_info = api_calls.get_jobseeker_profile(access_token=current_user.id)
    print(profile_info)
    resumes = api_calls.get_user_all_medias(access_token=current_user.id)

    if request.method == 'POST':
        if about_form.validate_on_submit():
            content = about_form.about.data
            res = api_calls.add_about_profile(content=content, access_token=current_user.id)
            return redirect(url_for('jobseeker_profile'))

        if education_form.validate_on_submit():
            education = {
                "institution_name": education_form.institution_name.data,
                "degree": education_form.degree.data,
                "field_of_study": education_form.field_of_study.data,
                "start_date": str(education_form.start_date.data),
                "end_date": str(education_form.end_date.data),
                "is_ongoing": education_form.ongoing.data
            }
            res = api_calls.add_education_profile(education=education, access_token=current_user.id)
            return redirect(url_for('jobseeker_profile'))

        if experience_form.validate_on_submit():
            experience = {
                "company_name": experience_form.company_name.data,
                "position": experience_form.position.data,
                "responsibilities": experience_form.responsibilities.data,
                "start_date": str(experience_form.start_date.data),
                "end_date": str(experience_form.end_date.data),
                "is_ongoing": experience_form.ongoing.data
            }
            res = api_calls.add_experience_profile(experience=experience, access_token=current_user.id)
            return redirect(url_for('jobseeker_profile'))

        if internship_form.validate_on_submit():
            internships = {
                "company_name": internship_form.company_name.data,
                "position": internship_form.position.data,
                "job_description": internship_form.job_description.data,
                "start_date": str(internship_form.start_date.data),
                "end_date": str(internship_form.end_date.data),
                "is_ongoing": internship_form.ongoing.data
            }
            res = api_calls.add_internships_profile(internships=internships, access_token=current_user.id)
            return redirect(url_for('jobseeker_profile'))

    return render_template('jobseeker/jobseeker_manage_profile.html', root_url=root_url, about_form=about_form,
                           education_form=education_form, experience_form=experience_form,
                           internship_form=internship_form, project_form=project_form, name_form=name_form,
                           email_form=email_form, phone_form=phone_form, accomplishment_form=accomplishment_form,
                           profile_picture_form=profile_picture_form,resumes=resumes, profile_info=profile_info)



@app.route('/jobseeker/add-accomplishment', methods=['GET', 'POST'])
@requires_any_permission("applicants")
@login_required
def jobseeker_add_accomplishment():
    accomplishment_form = forms.AccomplishmentForm()

    if request.method == 'POST':
        if accomplishment_form.validate_on_submit():
            accomplishments = {
                "title": accomplishment_form.title.data,
                "description": accomplishment_form.description.data,
                "achievement_date": str(accomplishment_form.achievement_date.data)
            }
            res = api_calls.add_accomplishments_profile(accomplishments=accomplishments, access_token=current_user.id)
            return redirect(url_for('jobseeker_profile'))



@app.route('/jobseeker/add-project', methods=['GET', 'POST'])
@requires_any_permission("applicants")
@login_required
def jobseeker_add_project():
    project_form = forms.ProjectForm()

    if request.method == 'POST':
        if project_form.validate_on_submit():
            projects = {
                "title": project_form.title.data,
                "description": project_form.description.data,
                "project_url": project_form.project_url.data,
            }
            res = api_calls.add_projects_profile(projects=projects, access_token=current_user.id)
            return redirect(url_for('jobseeker_profile'))


@app.route('/collect_jobseeker_name', methods=['GET', 'POST'])
@login_required
def collect_jobseeker_name():
    form = forms.CollectNameForm()
    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = form.lastname.data
        res = api_calls.update_basic_info(firstname=firstname,lastname=lastname, access_token=current_user.id)
        return redirect(url_for('jobseeker_profile'))


@app.route('/collect_jobseeker_email', methods=['GET', 'POST'])
@login_required
def collect_jobseeker_email():
    form = forms.CollectEmailForm()
    if form.validate_on_submit():
        email = form.email.data
        res = api_calls.update_basic_info(email=email, access_token=current_user.id)
        return redirect(url_for('jobseeker_profile'))

@app.route('/collect_jobseeker_phone', methods=['GET', 'POST'])
@login_required
def collect_jobseeker_phone():
    form = forms.CollectPhoneForm()
    if form.validate_on_submit():
        phone_number = form.phone_number.data
        res = api_calls.update_basic_info(phone_number=phone_number, access_token=current_user.id)
        return redirect(url_for('jobseeker_profile'))

@app.route('/collect_jobseeker_profile_picture', methods=['GET', 'POST'])
@login_required
def collect_jobseeker_profile_picture():
    print("ok")
    form = forms.CollectProfilePictureForm()
    if form.validate_on_submit():
        empty_folder(profile_pictures_folder)
        file = form.profile_picture.data

        filename = secure_filename(file.filename)
        # Save the file to a designated folder
        file_path = profile_pictures_folder + filename
        print(file_path)
        file.save(file_path)
        payload = {'profile_picture': (filename, open(file_path, 'rb'))}

        res = api_calls.update_basic_info(profile_picture=payload, access_token=current_user.id)
        if res:
            current_user.profile_picture = constants.BASE_URL+'/'+file_path
            print(current_user.profile_picture)
            session['profile_picture'] = constants.BASE_URL+'/'+file_path
            login_user(current_user)
        return redirect(url_for('jobseeker_profile'))
    else:
        print(form.errors)


@app.route('/delete-jobseeker-profile-info/<type>/<id>', methods=['GET', 'POST'])
@login_required
def delete_jobseeker_profile_info(type, id):
    try:
        res = api_calls.delete_jobseeker_profile_info(id=id,type=type, access_token=current_user.id)
        return redirect(url_for('jobseeker_profile'))
    except Exception as e:
        print(e)


@app.route('/view-jobseeker/<jobseeker_id>', methods=['GET', 'POST'])
def employer_view_jobseeker_profile(jobseeker_id):
    root_url = constants.ROOT_URL + '/'

    profile_info = api_calls.employer_view_jobseeker(jobseeker_id=jobseeker_id)

    return render_template('cms/job_openings/employer_view_jobseeker_profile.html', root_url=root_url,profile_info=profile_info)



@app.route('/jobs/search', methods=['GET', 'POST'])
def jobs_search():
    countries = ['United States', 'Canada', 'United Kingdom', 'Australia', 'Germany', 'France', 'India', 'China',
                 'Japan', 'Brazil', 'South Africa']
    job_types = [
        ('Full Time', 'Full Time'),
        ('Part Time', 'Part Time'),
        ('Training', 'Training'),
        ('Freelance', 'Freelance'),
        ('Seasonal', 'Seasonal'),
        ('Contract', 'Contract'),
        ('Temporary', 'Temporary')
    ]

    industries = [
            ('', 'Select Industry'),
            ('Accounting', 'Accounting'),
            ('Airlines/Aviation', 'Airlines/Aviation'),
            ('Alternative Dispute Resolution', 'Alternative Dispute Resolution'),
            ('Alternative Medicine', 'Alternative Medicine'),
            ('Animation', 'Animation'),
            ('Apparel & Fashion', 'Apparel & Fashion'),
            ('Architecture & Planning', 'Architecture & Planning'),
            ('Arts & Crafts', 'Arts & Crafts'),
            ('Automotive', 'Automotive'),
            ('Aviation & Aerospace', 'Aviation & Aerospace'),
            ('Banking', 'Banking'),
            ('Biotechnology', 'Biotechnology'),
            ('Broadcast Media', 'Broadcast Media'),
            ('Building Materials', 'Building Materials'),
            ('Business Supplies & Equipment', 'Business Supplies & Equipment'),
            ('Capital Markets', 'Capital Markets'),
            ('Chemicals', 'Chemicals'),
            ('Civic & Social Organization', 'Civic & Social Organization'),
            ('Civil Engineering', 'Civil Engineering'),
            ('Commercial Real Estate', 'Commercial Real Estate'),
            ('Computer & Network Security', 'Computer & Network Security'),
            ('Computer Games', 'Computer Games'),
            ('Computer Hardware', 'Computer Hardware'),
            ('Computer Networking', 'Computer Networking'),
            ('Computer Software', 'Computer Software'),
            ('Construction', 'Construction'),
            ('Consumer Electronics', 'Consumer Electronics'),
            ('Consumer Goods', 'Consumer Goods'),
            ('Consumer Services', 'Consumer Services'),
            ('Cosmetics', 'Cosmetics'),
            ('Dairy', 'Dairy'),
            ('Defense & Space', 'Defense & Space'),
            ('Design', 'Design'),
            ('Education Management', 'Education Management'),
            ('E-learning', 'E-learning'),
            ('Electrical & Electronic Manufacturing', 'Electrical & Electronic Manufacturing'),
            ('Entertainment', 'Entertainment'),
            ('Environmental Services', 'Environmental Services'),
            ('Events Services', 'Events Services'),
            ('Executive Office', 'Executive Office'),
            ('Facilities Services', 'Facilities Services'),
            ('Farming', 'Farming'),
            ('Financial Services', 'Financial Services'),
            ('Fine Art', 'Fine Art'),
            ('Fishery', 'Fishery'),
            ('Food & Beverages', 'Food & Beverages'),
            ('Food Production', 'Food Production'),
            ('Fundraising', 'Fundraising'),
            ('Furniture', 'Furniture'),
            ('Gambling & Casinos', 'Gambling & Casinos'),
            ('Glass, Ceramics & Concrete', 'Glass, Ceramics & Concrete'),
            ('Government Administration', 'Government Administration'),
            ('Government Relations', 'Government Relations'),
            ('Graphic Design', 'Graphic Design'),
            ('Health, Wellness & Fitness', 'Health, Wellness & Fitness'),
            ('Higher Education', 'Higher Education'),
            ('Hospital & Health Care', 'Hospital & Health Care'),
            ('Hospitality', 'Hospitality'),
            ('Human Resources', 'Human Resources'),
            ('Import & Export', 'Import & Export'),
            ('Individual & Family Services', 'Individual & Family Services'),
            ('Industrial Automation', 'Industrial Automation'),
            ('Information Services', 'Information Services'),
            ('Information Technology & Services', 'Information Technology & Services'),
            ('Insurance', 'Insurance'),
            ('International Affairs', 'International Affairs'),
            ('International Trade & Development', 'International Trade & Development'),
            ('Internet', 'Internet'),
            ('Investment Banking/Venture', 'Investment Banking/Venture'),
            ('Investment Management', 'Investment Management'),
            ('Judiciary', 'Judiciary'),
            ('Law Enforcement', 'Law Enforcement'),
            ('Law Practice', 'Law Practice'),
            ('Legal Services', 'Legal Services'),
            ('Legislative Office', 'Legislative Office'),
            ('Leisure & Travel', 'Leisure & Travel'),
            ('Libraries', 'Libraries'),
            ('Logistics & Supply Chain', 'Logistics & Supply Chain'),
            ('Luxury Goods & Jewelry', 'Luxury Goods & Jewelry'),
            ('Machinery', 'Machinery'),
            ('Management Consulting', 'Management Consulting'),
            ('Maritime', 'Maritime'),
            ('Marketing & Advertising', 'Marketing & Advertising'),
            ('Market Research', 'Market Research'),
            ('Mechanical or Industrial Engineering', 'Mechanical or Industrial Engineering'),
            ('Media Production', 'Media Production'),
            ('Medical Device', 'Medical Device'),
            ('Medical Practice', 'Medical Practice'),
            ('Mental Health Care', 'Mental Health Care'),
            ('Military', 'Military'),
            ('Mining & Metals', 'Mining & Metals'),
            ('Motion Pictures & Film', 'Motion Pictures & Film'),
            ('Museums & Institutions', 'Museums & Institutions'),
            ('Music', 'Music'),
            ('Nanotechnology', 'Nanotechnology'),
            ('Newspapers', 'Newspapers'),
            ('Nonprofit Organization Management', 'Nonprofit Organization Management'),
            ('Oil & Energy', 'Oil & Energy'),
            ('Online Publishing', 'Online Publishing'),
            ('Outsourcing/Offshoring', 'Outsourcing/Offshoring'),
            ('Package/Freight Delivery', 'Package/Freight Delivery'),
            ('Packaging & Containers', 'Packaging & Containers'),
            ('Paper & Forest Products', 'Paper & Forest Products'),
            ('Performing Arts', 'Performing Arts'),
            ('Pharmaceuticals', 'Pharmaceuticals'),
            ('Philanthropy', 'Philanthropy'),
            ('Photography', 'Photography'),
            ('Plastics', 'Plastics'),
            ('Political Organization', 'Political Organization'),
            ('Primary/Secondary', 'Primary/Secondary'),
            ('Printing', 'Printing'),
            ('Professional Training', 'Professional Training'),
            ('Program Development', 'Program Development'),
            ('Public Policy', 'Public Policy'),
            ('Public Relations', 'Public Relations'),
            ('Public Safety', 'Public Safety'),
            ('Publishing', 'Publishing'),
            ('Railroad Manufacture', 'Railroad Manufacture'),
            ('Ranching', 'Ranching'),
            ('Real Estate', 'Real Estate'),
            ('Recreational', 'Recreational'),
            ('Facilities & Services', 'Facilities & Services'),
            ('Religious Institutions', 'Religious Institutions'),
            ('Renewables & Environment', 'Renewables & Environment'),
            ('Research', 'Research'),
            ('Restaurants', 'Restaurants'),
            ('Retail', 'Retail'),
            ('Security & Investigations', 'Security & Investigations'),
            ('Semiconductors', 'Semiconductors'),
            ('Shipbuilding', 'Shipbuilding'),
            ('Sporting Goods', 'Sporting Goods'),
            ('Sports', 'Sports'),
            ('Staffing & Recruiting', 'Staffing & Recruiting'),
            ('Supermarkets', 'Supermarkets'),
            ('Telecommunications', 'Telecommunications'),
            ('Textiles', 'Textiles'),
            ('Think Tanks', 'Think Tanks'),
            ('Tobacco', 'Tobacco'),
            ('Translation & Localization', 'Translation & Localization'),
            ('Transportation/Trucking/Railroad', 'Transportation/Trucking/Railroad'),
            ('Utilities', 'Utilities'),
            ('Venture Capital', 'Venture Capital'),
            ('Veterinary', 'Veterinary'),
            ('Warehousing', 'Warehousing'),
            ('Wholesale', 'Wholesale'),
            ('Wine & Spirits', 'Wine & Spirits'),
            ('Wireless', 'Wireless'),
            ('Writing & Editing', 'Writing & Editing')
    ]

    jobs=[]


    if request.method == 'GET':
        # Extract query parameters
        country = request.args.get('country')
        state = request.args.get('state')
        job_type = request.args.get('job_type')
        industry = request.args.get('industry')
        date_filter = request.args.get('date_filter')
        keyword = request.args.get('keyword')

        prefilled_data = {
            'keyword': keyword,
            'country': country,
            'state': state,
            'job_type': job_type,
            'industry': industry,
            'date_filter': date_filter
        }


        # if country or state or job_type or industry or date_filter or keyword:
        jobs = api_calls.get_filtered_jobs(country=country, state=state, job_type=job_type, industry=industry, date_filter=date_filter, keyword=keyword)
        print(jobs)

    return render_template('jobseeker/jobs_search_2.html', countries=countries, job_types=job_types, industries=industries, jobs=jobs, prefilled_data=prefilled_data)



@app.route('/jobs/filter', methods=['GET', 'POST'])
def jobs_filter():
    countries = ['United States', 'Canada', 'United Kingdom', 'Australia', 'Germany', 'France', 'India', 'China',
                 'Japan', 'Brazil', 'South Africa']
    job_types = [
        ('Full Time', 'Full Time'),
        ('Part Time', 'Part Time'),
        ('Training', 'Training'),
        ('Freelance', 'Freelance'),
        ('Seasonal', 'Seasonal'),
        ('Contract', 'Contract'),
        ('Temporary', 'Temporary')
    ]

    industries = [
            ('', 'Select Industry'),
            ('Accounting', 'Accounting'),
            ('Airlines/Aviation', 'Airlines/Aviation'),
            ('Alternative Dispute Resolution', 'Alternative Dispute Resolution'),
            ('Alternative Medicine', 'Alternative Medicine'),
            ('Animation', 'Animation'),
            ('Apparel & Fashion', 'Apparel & Fashion'),
            ('Architecture & Planning', 'Architecture & Planning'),
            ('Arts & Crafts', 'Arts & Crafts'),
            ('Automotive', 'Automotive'),
            ('Aviation & Aerospace', 'Aviation & Aerospace'),
            ('Banking', 'Banking'),
            ('Biotechnology', 'Biotechnology'),
            ('Broadcast Media', 'Broadcast Media'),
            ('Building Materials', 'Building Materials'),
            ('Business Supplies & Equipment', 'Business Supplies & Equipment'),
            ('Capital Markets', 'Capital Markets'),
            ('Chemicals', 'Chemicals'),
            ('Civic & Social Organization', 'Civic & Social Organization'),
            ('Civil Engineering', 'Civil Engineering'),
            ('Commercial Real Estate', 'Commercial Real Estate'),
            ('Computer & Network Security', 'Computer & Network Security'),
            ('Computer Games', 'Computer Games'),
            ('Computer Hardware', 'Computer Hardware'),
            ('Computer Networking', 'Computer Networking'),
            ('Computer Software', 'Computer Software'),
            ('Construction', 'Construction'),
            ('Consumer Electronics', 'Consumer Electronics'),
            ('Consumer Goods', 'Consumer Goods'),
            ('Consumer Services', 'Consumer Services'),
            ('Cosmetics', 'Cosmetics'),
            ('Dairy', 'Dairy'),
            ('Defense & Space', 'Defense & Space'),
            ('Design', 'Design'),
            ('Education Management', 'Education Management'),
            ('E-learning', 'E-learning'),
            ('Electrical & Electronic Manufacturing', 'Electrical & Electronic Manufacturing'),
            ('Entertainment', 'Entertainment'),
            ('Environmental Services', 'Environmental Services'),
            ('Events Services', 'Events Services'),
            ('Executive Office', 'Executive Office'),
            ('Facilities Services', 'Facilities Services'),
            ('Farming', 'Farming'),
            ('Financial Services', 'Financial Services'),
            ('Fine Art', 'Fine Art'),
            ('Fishery', 'Fishery'),
            ('Food & Beverages', 'Food & Beverages'),
            ('Food Production', 'Food Production'),
            ('Fundraising', 'Fundraising'),
            ('Furniture', 'Furniture'),
            ('Gambling & Casinos', 'Gambling & Casinos'),
            ('Glass, Ceramics & Concrete', 'Glass, Ceramics & Concrete'),
            ('Government Administration', 'Government Administration'),
            ('Government Relations', 'Government Relations'),
            ('Graphic Design', 'Graphic Design'),
            ('Health, Wellness & Fitness', 'Health, Wellness & Fitness'),
            ('Higher Education', 'Higher Education'),
            ('Hospital & Health Care', 'Hospital & Health Care'),
            ('Hospitality', 'Hospitality'),
            ('Human Resources', 'Human Resources'),
            ('Import & Export', 'Import & Export'),
            ('Individual & Family Services', 'Individual & Family Services'),
            ('Industrial Automation', 'Industrial Automation'),
            ('Information Services', 'Information Services'),
            ('Information Technology & Services', 'Information Technology & Services'),
            ('Insurance', 'Insurance'),
            ('International Affairs', 'International Affairs'),
            ('International Trade & Development', 'International Trade & Development'),
            ('Internet', 'Internet'),
            ('Investment Banking/Venture', 'Investment Banking/Venture'),
            ('Investment Management', 'Investment Management'),
            ('Judiciary', 'Judiciary'),
            ('Law Enforcement', 'Law Enforcement'),
            ('Law Practice', 'Law Practice'),
            ('Legal Services', 'Legal Services'),
            ('Legislative Office', 'Legislative Office'),
            ('Leisure & Travel', 'Leisure & Travel'),
            ('Libraries', 'Libraries'),
            ('Logistics & Supply Chain', 'Logistics & Supply Chain'),
            ('Luxury Goods & Jewelry', 'Luxury Goods & Jewelry'),
            ('Machinery', 'Machinery'),
            ('Management Consulting', 'Management Consulting'),
            ('Maritime', 'Maritime'),
            ('Marketing & Advertising', 'Marketing & Advertising'),
            ('Market Research', 'Market Research'),
            ('Mechanical or Industrial Engineering', 'Mechanical or Industrial Engineering'),
            ('Media Production', 'Media Production'),
            ('Medical Device', 'Medical Device'),
            ('Medical Practice', 'Medical Practice'),
            ('Mental Health Care', 'Mental Health Care'),
            ('Military', 'Military'),
            ('Mining & Metals', 'Mining & Metals'),
            ('Motion Pictures & Film', 'Motion Pictures & Film'),
            ('Museums & Institutions', 'Museums & Institutions'),
            ('Music', 'Music'),
            ('Nanotechnology', 'Nanotechnology'),
            ('Newspapers', 'Newspapers'),
            ('Nonprofit Organization Management', 'Nonprofit Organization Management'),
            ('Oil & Energy', 'Oil & Energy'),
            ('Online Publishing', 'Online Publishing'),
            ('Outsourcing/Offshoring', 'Outsourcing/Offshoring'),
            ('Package/Freight Delivery', 'Package/Freight Delivery'),
            ('Packaging & Containers', 'Packaging & Containers'),
            ('Paper & Forest Products', 'Paper & Forest Products'),
            ('Performing Arts', 'Performing Arts'),
            ('Pharmaceuticals', 'Pharmaceuticals'),
            ('Philanthropy', 'Philanthropy'),
            ('Photography', 'Photography'),
            ('Plastics', 'Plastics'),
            ('Political Organization', 'Political Organization'),
            ('Primary/Secondary', 'Primary/Secondary'),
            ('Printing', 'Printing'),
            ('Professional Training', 'Professional Training'),
            ('Program Development', 'Program Development'),
            ('Public Policy', 'Public Policy'),
            ('Public Relations', 'Public Relations'),
            ('Public Safety', 'Public Safety'),
            ('Publishing', 'Publishing'),
            ('Railroad Manufacture', 'Railroad Manufacture'),
            ('Ranching', 'Ranching'),
            ('Real Estate', 'Real Estate'),
            ('Recreational', 'Recreational'),
            ('Facilities & Services', 'Facilities & Services'),
            ('Religious Institutions', 'Religious Institutions'),
            ('Renewables & Environment', 'Renewables & Environment'),
            ('Research', 'Research'),
            ('Restaurants', 'Restaurants'),
            ('Retail', 'Retail'),
            ('Security & Investigations', 'Security & Investigations'),
            ('Semiconductors', 'Semiconductors'),
            ('Shipbuilding', 'Shipbuilding'),
            ('Sporting Goods', 'Sporting Goods'),
            ('Sports', 'Sports'),
            ('Staffing & Recruiting', 'Staffing & Recruiting'),
            ('Supermarkets', 'Supermarkets'),
            ('Telecommunications', 'Telecommunications'),
            ('Textiles', 'Textiles'),
            ('Think Tanks', 'Think Tanks'),
            ('Tobacco', 'Tobacco'),
            ('Translation & Localization', 'Translation & Localization'),
            ('Transportation/Trucking/Railroad', 'Transportation/Trucking/Railroad'),
            ('Utilities', 'Utilities'),
            ('Venture Capital', 'Venture Capital'),
            ('Veterinary', 'Veterinary'),
            ('Warehousing', 'Warehousing'),
            ('Wholesale', 'Wholesale'),
            ('Wine & Spirits', 'Wine & Spirits'),
            ('Wireless', 'Wireless'),
            ('Writing & Editing', 'Writing & Editing')
    ]

    if request.method == 'GET':
        # Extract query parameters
        country = request.args.get('country') or ''
        state = request.args.get('state') or ''
        job_type = request.args.get('job_type') or ''
        industry = request.args.get('industry') or ''
        date_filter = request.args.get('date_filter') or ''
        keyword= request.args.get('keyword') or ''

        prefilled_data = {
            'keyword': keyword,
            'country': country,
            'state': state,
            'job_type': job_type,
            'industry': industry,
            'date_filter': date_filter
        }

        if country or state or job_type or industry or date_filter or keyword:
            jobs = api_calls.get_filtered_jobs(country=country, state=state, job_type=job_type, industry=industry, date_filter=date_filter, keyword=keyword)
            return redirect(url_for('job_search'))

    return render_template('jobseeker/jobs_search_1.html', countries=countries, job_types=job_types, industries=industries, prefilled_data=prefilled_data)



@app.route('/applicants/filter', methods=['GET', 'POST'])
def applicants_filter():
    job_types = static_dropdowns.job_types
    industries = static_dropdowns.industries
    companies = api_calls.admin_get_all_companies()
    if companies.status_code == 200:
        companies = companies.json()
    else:
        companies = []

    if request.method == 'GET':
        # Extract query parameters
        name = request.args.get('name')
        email = request.args.get('email')
        company = request.args.get('company')
        job_title =request.args.get('job_title')
        job_type = request.args.get('job_type')
        industry = request.args.get('industry')
        start_date = request.args.get('application_start_date')
        end_date = request.args.get('application_end_date')


        if name or email or job_type or industry or company or job_title or job_type or start_date or end_date:
            return redirect(url_for('applicants_search',
                                    name=name,
                                    email=email,
                                    company=company,
                                    job_title=job_title,
                                    job_type=job_type,
                                    industry=industry,
                                    application_start_date=start_date,
                                    application_end_date=end_date))




    return render_template('admin/applicant_search.html', job_types=job_types, companies=companies, industries=industries)

@app.route('/applicants/search', methods=['GET', 'POST'])
def applicants_search():
    job_types = static_dropdowns.job_types
    industries = static_dropdowns.industries
    companies = api_calls.admin_get_all_companies()
    if companies.status_code == 200:
        companies = companies.json()
    else:
        companies = []

    if request.method == 'GET':
        # Extract query parameters
        name = request.args.get('name')
        email = request.args.get('email')
        company = request.args.get('company')
        job_title =request.args.get('job_title')
        job_type = request.args.get('job_type')
        industry = request.args.get('industry')
        start_date = request.args.get('application_start_date')
        end_date = request.args.get('application_end_date')

        applicants=[]

        params = {}
        if name:
            params['name'] = name
        if email:
            params['email'] = email
        if company:
            params['company'] = company
        if job_title:
            params['job_title'] = job_title
        if job_type:
            params['job_type'] = job_type
        if industry:
            params['industry'] = industry
        if start_date:
            params['application_start_date'] = start_date
        if end_date:
            params['application_end_date'] = end_date


        if name or email or job_type or industry or company or job_title or job_type or start_date or end_date:

            applicants = api_calls.get_filtered_applicants(params = params)
            print(applicants)

    return render_template('admin/applicant_results.html', job_types=job_types, companies=companies, industries=industries, applicants=applicants)


@app.route('/employer/applicants/filter', methods=['GET', 'POST'])
def employer_applicants_filter():
    job_types = static_dropdowns.job_types
    industries = static_dropdowns.industries

    if request.method == 'POST':
        # Extract query parameters
        name = request.args.get('name')
        email = request.args.get('email')
        job_title =request.args.get('job_title')
        job_type = request.args.get('job_type')
        industry = request.args.get('industry')
        start_date = request.args.get('application_start_date')
        end_date = request.args.get('application_end_date')

        return redirect(url_for('employer_applicants_search',
                                    name=name,
                                    email=email,
                                    job_title=job_title,
                                    job_type=job_type,
                                    industry=industry,
                                    application_start_date=start_date,
                                    application_end_date=end_date))




    return render_template('cms/employer/applicant_search.html', job_types=job_types, industries=industries)


@app.route('/employer/applicants/search', methods=['GET', 'POST'])
def employer_applicants_search():
    job_types = static_dropdowns.job_types
    industries = static_dropdowns.industries
    statuses = api_calls.get_applicant_trackers(access_token=current_user.id)
    if statuses is None:
        statuses = static_dropdowns.statuses

    print('here')

    if request.method == 'GET':
        # Extract query parameters
        name = request.args.get('name')
        email = request.args.get('email')
        job_title =request.args.get('job_title')
        job_type = request.args.get('job_type')
        industry = request.args.get('industry')
        start_date = request.args.get('application_start_date')
        end_date = request.args.get('application_end_date')

        applicants=[]

        params = {}
        if name:
            params['name'] = name
        if email:
            params['email'] = email
        if job_title:
            params['job_title'] = job_title
        if job_type:
            params['job_type'] = job_type
        if industry:
            params['industry'] = industry
        if start_date:
            params['application_start_date'] = start_date
        if end_date:
            params['application_end_date'] = end_date

        print('here')
        applicants = api_calls.get_filtered_applicants_for_employer(params = params,access_token=current_user.id)
        print(applicants)
        print(len(applicants))
    return render_template('cms/employer/applicant_results.html', job_types=job_types, industries=industries, result=applicants, statuses=statuses)



@app.route('/jobseeker/filter', methods=['GET', 'POST'])
def jobseekers_filter():
    if request.method == 'GET':
        # Extract query parameters
        name = request.args.get('name')
        email = request.args.get('email')
        jobseeker_id = request.args.get('jobseeker_id')
        phone_no = request.args.get('phone_no')



        if name or email or jobseeker_id or phone_no:
            return redirect(url_for('jobseekers_search',
                                    name=name,
                                    email=email,
                                    jobseeker_id=jobseeker_id,
                                    phone_no=phone_no
                                    ))

    return render_template('admin/jobseeker_search.html')


@app.route('/jobseeker/search', methods=['GET', 'POST'])
def jobseekers_search():
    if request.method == 'GET':
        # Extract query parameters
        name = request.args.get('name')
        email = request.args.get('email')
        jobseeker_id = int(request.args.get('jobseeker_id')) if request.args.get('jobseeker_id') != '' else None
        phone_no = request.args.get('phone_no')
        print(name)
        print(email)
        print(jobseeker_id)
        print(phone_no)
        print('inside if request method get')


        jobseekers = []
        if name or email or jobseeker_id or phone_no:
            print('going to make api call')
            jobseekers= api_calls.get_filtered_jobseekers(name=name,email=email,jobseeker_id=jobseeker_id,phone_no=phone_no)

    return render_template('admin/jobseeker_search_results.html', jobseekers=jobseekers)




@app.route('/admin/stats')
@requires_any_permission("manage_user")
@login_required
def admin_stats():
    data = api_calls.get_admin_stats() or {}
    return render_template('admin/admin_stats_reports.html', data=data)


@app.route('/reports')
@requires_any_permission("manage_posts")
@login_required
def employer_reports():
    stats = api_calls.get_employer_reports(access_token=current_user.id) or {}
    total_jobs = stats["total_jobs"]
    total_views = stats["total_views"]
    applicants_count = stats["applicants_count"]
    in_progress_jobs = stats["in_progress_jobs"]
    statuses = stats["statuses"]

    # Add these new fields
    jobs_by_industry = stats["jobs_by_industry"]
    jobs_by_views = stats["jobs_by_views"]
    jobs_by_applicants = stats["jobs_by_applicants"]

    return render_template('cms/employer/employer_reports.html',
                           total_jobs=total_jobs, total_views=total_views,
                           applicants_count=applicants_count, in_progress_jobs=in_progress_jobs,
                           statuses=statuses, jobs_by_industry=jobs_by_industry,
                           jobs_by_views=jobs_by_views, jobs_by_applicants=jobs_by_applicants)


@app.route('/homepage_contact_form_submission', methods=['POST'])
def homepage_contactus_submission():
    try:
        data = request.get_json()

        # Extract form fields
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')
        recaptcha_token = data.get('g-recaptcha-response')  # Extract reCAPTCHA token
        is_token_valid = verify_recaptcha(recaptcha_token)
        if is_token_valid:
            result = api_calls.homepage_contact_form_submission(name=name, email=email, message=message)
        return jsonify({'message': 'Form submitted successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'An error occurred while processing the form'}), 500


@app.route('/aboutus')
def about_us():
    return render_template('aboutus.html')


################## ADMIN CmS ####################################################


@app.route('/posts')
def all_cms_post():
    result = api_calls.get_all_posts()
    if result is None:
        result = []  # Set result to an empty list
    print(result)

    return render_template('all_posts.html', result=result)

@app.route('/posts/category/<category>')
def cms_posts_by_category(category):
    result = api_calls.get_post_by_category(category)
    if result is None:
        result = []  # Set result to an empty list
    print(result)

    return render_template('admin/admin_cms/posts_by_category.html', category=category,result=result)

@app.route('/posts/subcategory/<subcategory>')
def cms_posts_by_subcategory(subcategory):
    result = api_calls.get_post_by_subcategory(subcategory)
    if result is None:
        result = []  # Set result to an empty list
    print(result)

    return render_template('admin/admin_cms/posts_by_subcategory.html', subcategory=subcategory,result=result)

@app.route('/posts/tag/<tag>')
def cms_posts_by_tag(tag):
    result = api_calls.get_post_by_tag(tag)
    if result is None:
        result = []  # Set result to an empty list
    print(result)

    return render_template('admin/admin_cms/posts_by_tag.html', tag=tag,result=result)




@app.route('/admin/cms/posts')
@requires_any_permission("manage_user")
@login_required
def admin_all_cms_post():
    result = api_calls.get_admin_all_posts(access_token=current_user.id)
    if result is None:
        result = []  # Set result to an empty list

    return render_template('admin/admin_cms/cms_all_post.html', result=result)


@app.route("/admin/delete-posts/<post_id>", methods=['GET', 'POST'])
@login_required
def admin_delete_cms_post(post_id):
    result = api_calls.admin_delete_post(post_id=post_id, access_token=current_user.id)

    # Print the status code for debugging purposes
    print(result.status_code)

    if result.status_code == 200:
        flash('Post deleted successfully', category='info')
        return redirect(url_for('admin_all_cms_post'))
    else:
        abort(response.status_code)

@app.route('/admin/cms/create-post/', methods=['GET', 'POST'])
@requires_any_permission("manage_user")
@login_required
def add_cms_post():
    form = forms.AddPost()
    media_form = forms.AddMediaForm()

    # Fetch categories and format them for the form choices
    try:
        categories = api_calls.get_cms_all_categories(access_token=current_user.id)
        category_choices = [('', 'Select a category')] + [(category['id'], category['category']) for category in categories]
    except Exception as e:
        print(f"Error fetching categories: {e}")
        category_choices = [('', 'Select Category')]

    form.category.choices = category_choices

    if form.category.data:
        # Fetch subcategories based on the selected category
        try:
            subcategories = api_calls.get_subcategories_by_category(form.category.data)
            subcategory_choices = [(subcategory['id'], subcategory['subcategory']) for subcategory in subcategories]
        except Exception as e:
            print(f"Error fetching subcategories: {e}")
            subcategory_choices = [('', 'Select Subcategory')]
        form.subcategory.choices = subcategory_choices

    if form.validate_on_submit():

        # if form.preview.data:
        #     return redirect(url_for('preview_post', username=current_user.username, root_url=ROOT_URL.replace('http://', '').replace('/', '')))
        tags = form.tags.data

        # Split tags into a list
        tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]

        post_data = {
            'title': form.title.data,
            'content': form.content.data,
            'category_id': form.category.data,
            'subcategory_id': form.subcategory.data,
            'access_token': current_user.id,
            'tags': tags_list
        }

        try:
            if form.save_draft.data:
                post_data['status'] = 'draft'
            elif form.publish.data:
                post_data['status'] = 'published'

            result = api_calls.create_post(**post_data)

            if result:
                # if form.publish.data:
                #     flash("Post created successfully", "success")
                #     try:
                #         post_slug = result["slug"]
                #         dateiso = result["created_at"]
                #         date = dateiso.split('T')[0]
                #         post_url = f'{constants.MY_ROOT_URL}/{current_user.username}/posts/{date}/{post_slug}'
                #         api_calls.send_newsletter(access_token=current_user.id, subject=form.title.data, body=form.content.data, post_url=post_url)
                #     except Exception as e:
                #         print(f"Problem sending newsletter: {e}")
                return redirect(url_for('admin_all_cms_post'))
            else:
                flash("Failed to create post", "danger")
        except Exception as e:
            flash(f"Error creating post: {e}", "danger")

    # Fetch media and forms
    root_url = constants.ROOT_URL + '/'
    # media_result = api_calls.get_user_all_medias(access_token=current_user.id) or []
    # forms_result = api_calls.get_user_all_forms(access_token=current_user.id) or []

    # Check if service is allowed for the user
    # if current_user.role == 'user':
    #     is_service_allowed = api_calls.is_service_access_allowed(current_user.id)
    #     if not is_service_allowed:
    #         return redirect(url_for('user_view_plan'))

    return render_template('admin/admin_cms/cms_add_post.html', form=form, media_form=media_form,categories=category_choices)


@app.route("/admin/cms/add-category/", methods=['GET', 'POST'])
@requires_any_permission("manage_user")
@login_required
def add_category():
    form = forms.AddCategory()
    if form.validate_on_submit():
        category = form.category.data
        response = api_calls.add_category(category, access_token=current_user.id)
        print(response.status_code)
        if (response.status_code == 200):
            flash('Category added Successful', category='info')
            return redirect(url_for('admin_cms_all_categories'))
        else:
            flash('Some problem occured', category='error')

    return render_template('admin/admin_cms/cms_add_category.html', form=form)


@app.route("/admin/cms/update-category/<category_id>/", methods=['GET', 'POST'])
@requires_any_permission("manage_user")
@login_required
def update_category(category_id):
    form = forms.AddCategory()
    if form.validate_on_submit():
        category = form.category.data
        response = api_calls.update_category(category_id, category, access_token=current_user.id)
        print(response.status_code)
        if (response.status_code == 200):
            flash('Category updated Successful', category='info')
            return redirect(url_for('admin_cms_all_categories'))
        else:
            flash('Some problem occured', category='error')

    return render_template('update_user_category.html', ROOT_URL=ROOT_URL, form=form, category_id=category_id)


@app.route('/admin/cms/categories')
@requires_any_permission("manage_user")
@login_required
def admin_cms_all_categories():
    result = api_calls.get_cms_all_categories(access_token=current_user.id)
    if result is None:
        result = []  # Set result to an empty list
    print(result)

    return render_template('admin/admin_cms/cms_all_categories.html', result=result)


@app.route('/admin/cms/all-subcategories/<category_id>')
@requires_any_permission("manage_user")
@login_required
def admin_cms_all_subcategory(category_id):
    result = api_calls.get_subcategories_by_category(category_id=category_id)
    if result is None:
        result = []  # Set result to an empty list
    print(result)

    return render_template('admin/admin_cms/cms_all_subcategories.html', result=result)


@app.route("/admin/cms/delete-category/<category_id>", methods=['GET', 'POST'])
@requires_any_permission("manage_user")
@login_required
def admin_cms_delete_category(category_id):
    result = api_calls.cms_delete_category(category_id=category_id, access_token=current_user.id)
    print(result.status_code)
    if result.status_code == 200:
        return redirect(url_for('admin_cms_all_categories'))
    else:
        abort(result.status_code)


@app.route('/admin/cms/subcategories/<int:category_id>')
def get_subcategories(category_id):
    # Fetch subcategories based on the category_id
    subcategories = api_calls.get_subcategories_by_category(category_id)
    return jsonify({'subcategories': subcategories})


@app.route("/admin/cms/add-subcategory/", methods=['GET', 'POST'])
@requires_any_permission("manage_user")
@login_required
def add_subcategory():
    form = forms.AddSubcategory()
    categories = api_calls.get_cms_all_categories(access_token=current_user.id)
    category_choices = [(category['id'], category['category']) for category in categories]
    form.category.choices = category_choices
    if form.validate_on_submit():
        subcategory = form.subcategory.data
        category_id = form.category.data
        response = api_calls.add_subcategory(subcategory, category_id, access_token=current_user.id)
        print(response.status_code)
        if (response.status_code == 200):
            flash('Subcategory added Successful', category='info')
            return redirect(url_for('admin_cms_all_categories'))
        else:
            flash('Some problem occured', category='error')

    return render_template('admin/admin_cms/cms_add_subcategory.html', ROOT_URL=ROOT_URL, form=form, categories=category_choices)


@app.route("/admin/cms/update-subcategory/<subcategory_id>", methods=['GET', 'POST'])
@requires_any_permission("manage_users")
@login_required
def update_subcategory(subcategory_id):
    form = forms.AddSubcategory()  # Assuming you have a form for subcategory
    categories = api_calls.get_cms_all_categories(access_token=current_user.id)
    category_choices = [(category['id'], category['category']) for category in categories]
    form.category.choices = category_choices
    if form.validate_on_submit():
        subcategory = form.subcategory.data
        category_id = form.category.data
        response = api_calls.update_subcategory(subcategory_id, subcategory, category_id, access_token=current_user.id)
        print(response.status_code)
        if (response.status_code == 200):
            flash('Subcategory added Successful', category='info')
            return redirect(url_for('admin_cms_all_categories'))
        else:
            flash('Some problem occured', category='error')

    return render_template('update_user_subcategory.html', form=form, subcategory_id=subcategory_id,
                           categories=category_choices)


@app.route("/admin/cms/delete-subcategory/<subcategory_id>", methods=['GET', 'POST'])
@requires_any_permission("manage_user")
@login_required
def admin_cms_delete_subcategory(subcategory_id):
    result = api_calls.cms_delete_subcategory(subcategory_id=subcategory_id, access_token=current_user.id)
    print(result.status_code)
    if result.status_code == 200:
        return redirect(url_for('admin_cms_all_categories'))


@app.route('/admin/cms/update-post/<post_id>', methods=['GET', 'POST'])
@requires_any_permission("manage_user")
def admin_update_cms_post(post_id):
    form = forms.AddPost()
    post = api_calls.get_post(post_id=post_id)

    # Fetch categories and format them for the form choices
    try:
        categories = api_calls.get_cms_all_categories(access_token=current_user.id)
        category_choices = [(category['id'], category['category']) for category in categories]
        if not category_choices:
            category_choices = [('', 'Select Category')]
    except Exception as e:
        print(f"Error fetching categories: {e}")
        category_choices = [('', 'Select Category')]
    form.category.choices = category_choices

    # If a category is selected, fetch and set subcategories
    if form.category.data:
        try:
            subcategories = api_calls.get_subcategories_by_category(form.category.data)
            subcategory_choices = [(subcategory['id'], subcategory['subcategory']) for subcategory in subcategories]
            if not subcategory_choices:
                subcategory_choices = [('', 'Select Subcategory')]
        except Exception as e:
            print(f"Error fetching subcategories: {e}")
            subcategory_choices = [('', 'Select Subcategory')]
        form.subcategory.choices = subcategory_choices


    if form.validate_on_submit():
        tags = form.tags.data

        # Split tags into a list
        tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]

        title = form.title.data
        content = form.content.data
        category = form.category.data
        subcategory = form.subcategory.data


        if form.publish.data:
            try:
                result = api_calls.admin_update_post(
                    post_id=post_id,
                    title=title,
                    content=content,
                    category_id=category,
                    subcategory_id=subcategory,
                    status='published',
                    access_token=current_user.id,
                    tags=tags_list
                )
                return redirect(url_for('admin_all_cms_post'))

                # if result:
                #     print("success")
                #     try:
                #         dateiso = result["created_at"]
                #         post_slug = result["slug"]
                #         date = dateiso.split('T')[0]
                #         post_url = f'{constants.MY_ROOT_URL}/{current_user.username}/posts/{date}/{post_slug}'
                #         print(post_url)
                #         send_mails = api_calls.send_newsletter(access_token=current_user.id, subject=form.title.data,
                #                                                body=form.content.data, post_url=post_url)
                #     except Exception as e:
                #         raise 'Problem sending newsletter' + e
                #     print("Post updated successfully")
                #     if current_user.role == 'user':
                #         print("redirecting")
                #         return redirect(url_for('user_all_post'))
                #     else:
                #         return redirect(url_for('all_post'))
                # else:
                #     print("Failed to update post")
            except Exception as e:
                print(f"Error updating post: {e}")
        if form.save_draft.data:
            try:
                result = api_calls.admin_update_post(
                    post_id=post_id,
                    title=title,
                    content=content,
                    category_id=category,
                    subcategory_id=subcategory,
                    status='draft',
                    access_token=current_user.id,
                    tags= tags_list
                )
                return redirect(url_for('admin_all_cms_post'))
            except Exception as e:
                print(f"Error updating post: {e}")
    tags_string = ""
    for t in post['tags']:
        tags_string+=t["name"]+","



    form.title.data = post['title']
    form.category.data = post['category_id']
    form.subcategory.data = post['subcategory_id']
    form.content.data = post['content']
    form.tags.data= tags_string

    return render_template('admin/admin_cms/cms_update_post.html', form=form, post_id=post_id)


@app.route("/posts/<slug>", methods=['GET', 'POST'])
def read_post(slug):
    import html
    response = api_calls.get_post_by_slug(slug)

    response["content"] = html.unescape(response["content"])
    print(response["content"])
    return render_template('read_cms_post.html', post=response)


##################################################### JOBSEEKER CONTINUATION #########################################################

@app.route('/jobseeker-create-profile', methods=['GET', 'POST'])
# @requires_any_permission("applicants")
# @login_required
def jobseeker_create_profile():
    about_form = forms.AboutForm()
    education_form = forms.EducationForm()
    experience_form = forms.ExperienceForm()
    internship_form = forms.InternshipForm()
    project_form = forms.ProjectForm()
    accomplishment_form = forms.AccomplishmentForm()

    resume_json = session.get('resume_json', {})
    session.pop('resume_json', None)  # Clear session data after submission
    if not isinstance(resume_json, dict) or not resume_json:
        resume_json = {}
    if request.method == 'POST':
        if about_form.validate_on_submit() and education_form.validate_on_submit() and \
                experience_form.validate_on_submit() and internship_form.validate_on_submit() and \
                project_form.validate_on_submit() and accomplishment_form.validate_on_submit():

            # Process the form data (Save to DB or perform actions)
            flash('Profile submitted successfully!', 'success')
            return redirect(url_for('jobseeker_profile'))
        else:
            flash('Please correct the errors in the form.', 'danger')

    return render_template(
        'jobseeker/jobseeker_profile_stepper.html',
        about_form=about_form,
        education_form=education_form,
        experience_form=experience_form,
        internship_form=internship_form,
        project_form=project_form,
        accomplishment_form=accomplishment_form,
        resume_json = resume_json  # Send JSON to template
    )


@app.route('/jobseeker/jobseeker-update-profile', methods=['GET', 'POST'])
# @requires_any_permission("applicants")
# @login_required
def jobseeker_update_profile():
    about_form = forms.AboutForm()
    education_form = forms.EducationForm()
    experience_form = forms.ExperienceForm()
    internship_form = forms.InternshipForm()
    project_form = forms.ProjectForm()
    accomplishment_form = forms.AccomplishmentForm()


    resume_json = api_calls.get_jobseeker_profile(access_token=current_user.id)
    print(resume_json)
    if not isinstance(resume_json, dict) or not resume_json:
        resume_json = {}


    if request.method == 'POST':
        data = request.get_json()
        response = api_calls.update_jobseeker_profile_two(profile_data=data, access_token=current_user.id)
        return jsonify({"success": True, "message": "Profile submitted successfully!"}), 200


    return render_template(
        'jobseeker/jobseeker_update_profile_stepper.html',
        about_form=about_form,
        education_form=education_form,
        experience_form=experience_form,
        internship_form=internship_form,
        project_form=project_form,
        accomplishment_form=accomplishment_form,
        resume_json = resume_json  # Send JSON to template
    )



@app.route('/jobseeker/submit-profile', methods=['GET', 'POST'])
# @requires_any_permission("applicants")
# @login_required
def submit_jobseeker_profile():
    # Retrieve the JSON payload from the request
    if request.method == 'POST':
        data = request.get_json()

        api_calls.update_jobseeker_profile(profile_data=data, access_token=current_user.id)

        # For debugging: print the data to your server console/log
        print("Received jobseeker JSON:", data)

        # Return a simple response (could be JSON, text, etc.)
        return jsonify({"success": True, "message": "Profile submitted successfully!"}), 200

@app.route('/jobseeker-profile-choice', methods=['GET', 'POST'])
# @requires_any_permission("applicants")
# @login_required
def jobseeker_profile_choice():
    if request.method == 'POST':
        pdf_file = request.files.get('pdf_file')
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)  # Open PDF from memory
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"  # Extract text from each page

            resume_json = parse_single_resume(resume_text=text)
            session['resume_json'] = resume_json
            print('done')
            return redirect(url_for('jobseeker_create_profile'))

        except Exception as e:
            return redirect(url_for('jobseeker_profile_choice'))

        print("got pdf")

    return render_template(
        'jobseeker/jobseeker_create_profile_choice.html',
    )

#####################################################################################################################################

@app.route('/features/recruitment-software')
def recruitment_software():
    return render_template('features/recruitment_software.html')

@app.route('/features/applicant-tracking')
def applicant_tracking_feature():
    return render_template('features/applicant_tracking.html')

@app.route('/features/resume-parsing')
def resume_parsing_feature():
    return render_template('features/resume_parsing.html')

@app.route('/features/recruitment-crm')
def recruitment_crm():
    return render_template('features/recruitment_crm.html')

@app.route('/features/candidate-matching')
def candidate_matching():
    return render_template('features/candidate_matching.html')

@app.route('/features/ai-recruitment')
def ai_recruitment():
    return render_template('features/ai_recruitment.html')

@app.route('/AI/resume-screening')
def ai_resume_screening():
    return render_template('AI/resume_screening.html')

@app.route('/AI/candidate-matching')
def ai_candidate_matching():
    return render_template('AI/candidate_matching.html')

@app.route('/AI/chatbots')
def ai_chatbots():
    return render_template('AI/chatbots.html')

@app.route('/AI/recruitment-analytics')
def ai_recruitment_analytics():
    return render_template('AI/recruitment_analytics.html')

@app.route('/services/ai-recruitment')
def ai_recruitment_service():
    return render_template('services/ai_recruitment.html')

@app.route('/services/candidate-screening')
def candidate_screening_service():
    return render_template('services/candidate_screening.html')

@app.route('/services/resume-parsing')
def resume_parsing_service():
    return render_template('services/resume_parsing.html')

@app.route('/services/career-site')
def career_site_service():
    return render_template('services/career_site.html')

@app.route('/services/interview-scheduling')
def interview_scheduling_service():
    return render_template('services/interview_scheduling.html')

@app.route('/products/recruitment-software')
def recruitment_software_product():
    return render_template('products/recruitment_software.html')

@app.route('/products/applicant-tracking')
def applicant_tracking_product():
    return render_template('products/applicant_tracking.html')

@app.route('/products/recruitment-crm')
def recruitment_crm_product():
    return render_template('products/recruitment_crm.html')

@app.route('/products/staffing-software')
def staffing_software_product():
    return render_template('products/staffing_software.html')

@app.route('/products/job-board')
def job_board_product():
    return render_template('products/job_board.html')

@app.route('/AI-tools/ai-agents')
def ai_agents():
    return render_template('AI_tools/ai_agents.html')

@app.route('/AI-tools/recruitment-chatbots')
def recruitment_chatbots():
    return render_template('AI_tools/recruitment_chatbots.html')

@app.route('/AI-tools/ai-candidate-matching')
def ai_tools_candidate_matching():
    return render_template('AI_tools/ai_candidate_matching.html')

@app.route('/AI-tools/ai-job-matching')
def ai_job_matching():
    return render_template('AI_tools/ai_job_matching.html')

@app.route('/AI-tools/ai-interview')
def ai_interview():
    return render_template('AI_tools/ai_interview.html')

@app.route('/faqs')
def faqs():
    return render_template('faqs.html')

@app.route('/privacy-policy') 
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/terms-of-service')
def terms_of_service():
    return render_template('terms_of_service.html')


#####################################################################################################################################
############################################## ALL ROUTES ABOVE THIS ################################################################
################################################   SITEMAP.XML  #####################################################################
#####################################################################################################################################
@app.route('/sitemap')
def sitemap_html():
    try:
        sitemap_data = api_calls.get_sitemap_data()
        company_list = sitemap_data.get('companies', []) or []
        jobs_list = sitemap_data.get('jobs', []) or []
        posts_list = sitemap_data.get('posts', []) or []
    except Exception:
        print(Exception)
    # Return the sitemap as an XML response
    return render_template('sitemap.html', company_list=company_list, jobs_list=jobs_list, posts_list=posts_list)

@app.route('/sitemap/table')
def sitemap_table():
    return render_template('sitemap_table.html')

@app.route('/sitemap/<sitemap_key>/sitemap.xml')
def sitemap_by_key(sitemap_key):
    try:
        sitemap_data = api_calls.get_sitemap_data()
        company_list = sitemap_data.get('companies', []) or []
        jobs_list = sitemap_data.get('jobs', []) or []
        posts_list = sitemap_data.get('posts', []) or []
    except Exception:
        print(Exception)

    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>\n"""
    sitemap_xml += """<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n"""

    if sitemap_key == 'companies':
        for entry in company_list:
            sitemap_xml += f"""
            <url>
                <loc>{entry['url']}</loc>
                <lastmod>{entry['lastmod']}</lastmod>
                <priority>{entry['priority']}</priority>
            </url>"""
        sitemap_xml += "\n</urlset>"

    elif sitemap_key == 'jobs':
        for entry in jobs_list:
            sitemap_xml += f"""
            <url>
                <loc>{entry['url']}</loc>
                <lastmod>{entry['lastmod']}</lastmod>
                <priority>{entry['priority']}</priority>
            </url>"""
        sitemap_xml += "\n</urlset>"

    elif sitemap_key == 'posts':

        for entry in posts_list:
            sitemap_xml += f"""
            <url>
                <loc>{entry['url']}</loc>
                <lastmod>{entry['lastmod']}</lastmod>
                <priority>{entry['priority']}</priority>
            </url>"""

        sitemap_xml += "\n</urlset>"

    elif sitemap_key == 'pages':
        return send_file('templates/sitemap.xml', mimetype='application/xml')

    # Return the sitemap as an XML response
    return Response(sitemap_xml, mimetype="application/xml")


@app.route('/sitemap.xml')
def sitemap():
    try:
        sitemap_data = api_calls.get_sitemap_data()
        company_list = sitemap_data.get('companies', []) or []
        jobs_list = sitemap_data.get('jobs', []) or []
        posts_list = sitemap_data.get('posts', []) or []
    except Exception:
        print(Exception)

    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>\n"""
    sitemap_xml += """<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n"""

    for entry in company_list:
        sitemap_xml += f"""
    <url>
        <loc>{entry['url']}</loc>
        <lastmod>{entry['lastmod']}</lastmod>
        <priority>{entry['priority']}</priority>
    </url>"""

    for entry in jobs_list:
        sitemap_xml += f"""
    <url>
        <loc>{entry['url']}</loc>
        <lastmod>{entry['lastmod']}</lastmod>
        <priority>{entry['priority']}</priority>
    </url>"""

    for entry in posts_list:
        sitemap_xml += f"""
    <url>
        <loc>{entry['url']}</loc>
        <lastmod>{entry['lastmod']}</lastmod>
        <priority>{entry['priority']}</priority>
    </url>"""

    sitemap_xml += "\n</urlset>"



    # Return the sitemap as an XML response
    return Response(sitemap_xml, mimetype="application/xml")

@app.route('/robots.txt')
def robots_txt():
    return send_from_directory('static', 'robots.txt', mimetype='text/plain')




if __name__ == '__main__':
    app.run()
