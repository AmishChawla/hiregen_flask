import json
import pprint
from flask import abort
import requests
import constants


def user_login(email, password):
    print('trying2')
    data = {
        "username": email,
        "password": password
    }

    try:
        response = requests.post(constants.BASE_URL + '/login', data=data)
        print(response.text)
        print(constants.BASE_URL + '/login')
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def dashboard(file_list, access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.post(constants.BASE_URL + '/process-resume/', files=file_list, headers=headers)
        return response

    except requests.exceptions.RequestException as e:
        # Handle request errors
        print(f"Error: {e}")


def user_register(firstname, lastname, phone_number, email, password, city, ip):
    print('trying3')
    headers = {'Content-Type': 'application/json'}
    data = {
        "firstname": firstname,
        "lastname": lastname,
        "phone_number": phone_number,
        "email": email,
        "password": password,
        "role": "user",
        "city": city,
        "ip_address": ip
    }

    try:
        response = requests.post(constants.BASE_URL + f'/register', data=json.dumps(data), headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def admin_register(username, email, password):
    print('trying9')
    headers = {'Content-Type': 'application/json'}
    data = {
        "username": username,
        "email": email,
        "password": password,
        "role": "admin"
    }

    try:
        # response = requests.post(constants.BASE_URL + '/register', data=json.dumps(data), headers=headers)
        response = requests.post(constants.BASE_URL + '/register-admin', data=json.dumps(data), headers=headers)

        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_user_profile(access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.get(constants.BASE_URL + '/user-profile', headers=headers)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_all_users(access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + '/admin/users', headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")



def get_admin_all_sites(access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + '/admin/all-sites', headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def admin_login(email, password):
    print('trying3')
    data = {
        "username": email,
        "password": password
    }

    try:
        response = requests.post(constants.BASE_URL + '/admin/login', data=data)
        print(response.text)
        print(constants.BASE_URL + '/admin/login')

        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


# Endpoint only accessible to admin
def add_user(username, email, password, role, security_group, access_token: str):
    print('trying3')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    data = {
        "username": username,
        "email": email,
        "password": password,
        "role": role,
        "security_group": security_group
    }

    try:
        response = requests.post(constants.BASE_URL + '/admin/add-user', data=json.dumps(data), headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def admin_trash_user(access_token: str, user_id: int):
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.delete(constants.BASE_URL + f'/admin/trash-user/{user_id}', headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def admin_restore_user(access_token: str, user_id: int):
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.put(constants.BASE_URL + f'/admin/restore-user/{user_id}', headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def admin_delete_user_permanently(access_token: str, user_id: int):
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.delete(constants.BASE_URL + f'/admin/delete-user/{user_id}', headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def admin_get_any_user(access_token: str, user_id: int):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + f'/admin/view-user/{user_id}', headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def update_user_password(current_password, new_password, confirm_new_password, access_token: str):
    print('trying3')
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-type': 'application/json'

    }

    data = {
        "current_password": current_password,
        "new_password": new_password,
        "confirm_new_password": confirm_new_password
    }

    try:
        response = requests.put(constants.BASE_URL + '/update-password', params=data, headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def forgot_password(email):
    print('trying6')

    headers = {
        'Content-type': 'application/json'
    }
    data = {
        "email": email,
    }

    try:
        response = requests.post(constants.BASE_URL + '/forgot-password', params=data, headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def reset_password(token, new_password):
    print('trying7')

    headers = {
        'Content-type': 'application/json'
    }
    data = {
        "token": token,
        "new_password": new_password
    }

    try:
        response = requests.post(constants.BASE_URL + '/reset-password', params=data, headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def admin_edit_any_user(access_token: str, user_id: int, username, role, status):
    print("trying")
    headers = {'Authorization': f'Bearer {access_token}'}

    data = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "status": status
    }

    try:
        print("try")
        response = requests.put(constants.BASE_URL + f'/admin/edit-user', headers=headers, params=data)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def update_user_profile(
        token,
        firstname=None,
        lastname=None,
        phone_number=None,
        username=None,
        email=None,
        company_name=None,
        company_location=None,
        company_website=None,
        company_description=None,
        profile_picture=None,
        company_logo=None,
        password=None
):

    # Prepare the data to be sent
    form_data = {
        "firstname": firstname,
        "lastname": lastname,
        "phone_number": phone_number,
        "username": username,
        "email": email,
        "company_name": company_name,
        "company_location": company_location,
        "company_website": company_website,
        "company_description": company_description,
        "password": password
    }

    # Prepare the headers with the authorization token
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Prepare the files for profile picture and company logo
    files = {}
    if profile_picture:
        files["profile_picture"] = profile_picture
    if company_logo:
        files["company_logo"] = company_logo

    # Send POST request to FastAPI
    response = requests.put(constants.BASE_URL + f'/update-profile', data=form_data, files=files, headers=headers)

    return response



def get_companies():
    try:
        response = requests.get(constants.BASE_URL + f'/companies')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_company_details(company_id: int):
    try:
        response = requests.get(constants.BASE_URL + f'/company/{company_id}')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_company_details_by_slug(company_slug: str):
    try:
        response = requests.get(constants.BASE_URL + f'/companies/by-company-slug/{company_slug}')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_jobs_by_company_id(company_id: int):
    try:
        response = requests.get(constants.BASE_URL + f'/job_openings/company/{company_id}')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")

def get_company_details_by_subdomain(company_subdomain: str):
    try:
        response = requests.get(constants.BASE_URL + f'/companies/by-subdomain/{company_subdomain}')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")



def company_register(name, website_url, company_subdomain, logo, description, location, access_token):
    print('trying3')
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        "name": name,
        "website_url": website_url,
    }
    data = {
        "location": location,
        "description": description,
        "company_subdomain":company_subdomain
    }
    try:
        response = requests.post(constants.BASE_URL + f'/companies/create-company',data=data, params=params,files=logo, headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def services():
    try:
        response = requests.get(constants.BASE_URL + '/services/all-services')
        return response

    except requests.exceptions.RequestException as e:
        # Handle request errors
        print(f"Error: {e}")


def add_service(name, description):
    headers = {
        'Content-Type': 'application/json',
    }

    params = {
        "name": name,
        "description": description,
    }

    try:
        response = requests.post(constants.BASE_URL + '/services/create-service', params=params, headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def admin_delete_service(service_id: int):
    try:
        response = requests.delete(constants.BASE_URL + f'/services/delete-service/{service_id}')
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def admin_get_any_service(service_id: int):
    try:
        response = requests.get(constants.BASE_URL + f'/services/{service_id}')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def admin_edit_any_service(service_id, service_name, service_description):
    print("trying")

    data = {
        "name": service_name,
        "description": service_description
    }

    try:
        print("try")
        response = requests.put(constants.BASE_URL + f'/services/update-service/{service_id}', json=data)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def admin_get_resume_history():
    try:
        response = requests.get(constants.BASE_URL + '/admin/resume-history')
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def admin_get_all_companies():
    print("trying")
    try:
        print("try")
        response = requests.get(constants.BASE_URL + '/companies/')
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_trash_users(access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + '/admin/trash-users', headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")

def admin_delete_job(job_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.delete(constants.BASE_URL + f'/admin/jobs/delete-job/{job_id}', headers=headers)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def admin_delete_company(company_id: int):
    try:
        response = requests.delete(constants.BASE_URL + f'/companies/delete-company/{company_id}')
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def admin_get_any_company(company_id: int):
    try:
        response = requests.get(constants.BASE_URL + f'/companies/{company_id}')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def admin_edit_any_company(company_id, name, location):
    print("trying")

    data = {
        "name": name,
        "location": location
    }

    try:
        print("try")
        response = requests.put(constants.BASE_URL + f'/companies/update-company/{company_id}', params=data)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def admin_get_email_setup(access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        print("try")
        response = requests.get(constants.BASE_URL + f'/smtp_settings/', headers=headers)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")





def admin_update_email_setup(access_token: str, smtp_server, smtp_port, smtp_username, smtp_password, sender_email):
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {
        "smtp_server": smtp_server,
        "smtp_port": smtp_port,
        "smtp_username": smtp_username,
        "smtp_password": smtp_password,
        "sender_email": sender_email
    }

    try:
        response = requests.put(constants.BASE_URL + f'/admin/update-email-settings/', headers=headers, json=data)
        response.raise_for_status()  # Raises an HTTPError if the response was unsuccessful
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
        raise  # Re-raise the exception to be handled by the caller
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
        raise  # Re-raise the exception to be handled by the caller
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
        raise  # Re-raise the exception to be handled by the caller
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")
        raise  # Re-raise the exception to be handled by the caller


def admin_assign_service(user_id, service_ids: list):
    params = {
        "user_id": user_id

    }

    try:
        response = requests.post(constants.BASE_URL + f'/users/assign_services/', params=params, json=service_ids)
        response.raise_for_status()  # Raises an HTTPError if the response was unsuccessful
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
        raise  # Re-raise the exception to be handled by the caller
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
        raise  # Re-raise the exception to be handled by the caller
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
        raise  # Re-raise the exception to be handled by the caller
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")
        raise  # Re-raise the exception to be handled by the caller


def user_specific_services(user_id):
    try:
        print("try")
        response = requests.get(constants.BASE_URL + f'/users/{user_id}/services')
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


############################################################### PLANS ##############################################################################
def get_all_plans():
    try:
        response = requests.get(constants.BASE_URL + '/plans/')
        if response.status_code == 200:
            result = response.json()
            return result

    except requests.exceptions.RequestException as e:
        # Handle request errors
        print(f"Error: {e}")


def create_plan(plan_name, duration, price, job_postings, features, stripe_product_id=None, stripe_price_id=None):
    print("Inside API call for creating a plan")

    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        "plan_name": plan_name,
        "duration": duration,
        "price": price,
        "job_postings": job_postings,
        "ai_candidate_matching": features.get("ai_candidate_matching", False),
        "ai_based_resume_ranking": features.get("ai_based_resume_ranking", False),
        "applicant_tracking": features.get("applicant_tracking", False),
        "resume_parsing": features.get("resume_parsing", False),
        "analytics_and_reports": features.get("analytics_and_reports", False),
        "interview_scheduling": features.get("interview_scheduling", False),
        "multi_user_access": features.get("multi_user_access", False),
        "branded_careers_page": features.get("branded_careers_page", False),
    }

    try:
        response = requests.post(constants.BASE_URL + '/plans/create-plan', json=data, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)

        if response.status_code == 200:
            print("Plan created successfully!")
            return response.json()
        else:
            print(f"Failed to create plan. Status Code: {response.status_code}")
            return None

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")

    return None


def delete_plan(plan_id: int):
    try:
        response = requests.delete(constants.BASE_URL + f'/plans/delete-plan/{plan_id}')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_plan_by_id(plan_id: int):
    try:
        response = requests.get(constants.BASE_URL + f'/plans/{plan_id}')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def update_plan(plan_id: int, plan_name: str, time_period: str, fees: int, num_resume_parse: str, plan_details: str):
    data = {
        "plan_type_name": plan_name,
        "time_period": time_period,
        "fees": fees,
        "num_resume_parse": num_resume_parse,
        "plan_details": plan_details
    }
    try:
        print("try")
        response = requests.put(constants.BASE_URL + f'/plans/update-plan/{plan_id}', json=data)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


##################################################### SUBSCRIPTION #################################################################

def start_subscription(plan_id, stripe_token, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}

    params = {
        "plan_id": plan_id,
    }

    if stripe_token is not None:
        params["stripe_token"] = stripe_token

    try:
        print("try")
        response = requests.post(constants.BASE_URL + '/subscriptions/create-subscription', params=params, headers=headers)
        response.raise_for_status()  # This will raise an HTTPError for bad responses
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def cancel_subscription(subscription_id):
    try:
        print("try")
        response = requests.post(constants.BASE_URL + f'/subscriptions/{subscription_id}/cancel')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def resume_subscription(subscription_id):
    try:
        print("try")
        response = requests.post(constants.BASE_URL + f'/subscriptions/{subscription_id}/resume')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def purchase_history(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        print("try")
        response = requests.get(constants.BASE_URL + f'/subscriptions/purchase_history', headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_all_subscriptions(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        print("try")
        response = requests.get(constants.BASE_URL + f'/subscriptions/all-subscriptions', headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_all_posts():
    try:
        response = requests.get(constants.BASE_URL + '/all-posts/')
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result
        else:
            print("API Error:", response.text)  # Debug: Print error message from API
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_user_all_job_openings(access_token, maximum_posts: int = None):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        "maximum_posts": maximum_posts
    }
    try:
        response = requests.get(constants.BASE_URL + f'/company-all-job_openings', params=params, headers=headers)
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result

        else:
            print("API Error:", response.text)
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_all_job_openings_for_admin(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + f'/admin/all-job_openings', headers=headers)
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result

        else:
            print("API Error:", response.text)
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_all_jobseekers_for_admin(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + f'/jobseeker/admin/all-jobseekers/', headers=headers)
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result

        else:
            print("API Error:", response.text)
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")



def get_job_applicants(access_token, job_id):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + f'/jobs/{job_id}/applicants', headers=headers)
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result

        else:
            print("API Error:", response.text)

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_all_applicants(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + f'/all-applicants', headers=headers)
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result

        else:
            print("API Error:", response.text)

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")

def get_all_applicants_for_admin(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + f'/admin/all-applicants', headers=headers)
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result

        else:
            print("API Error:", response.text)

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")





def delete_job_opening(job_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.delete(constants.BASE_URL + f'/job_opening/delete-job/{job_id}', headers=headers)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def create_job_opening(job_detail, access_token):
    print('trying to create post')
    print("2")
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.post(constants.BASE_URL + '/job_opening/create-job', json=job_detail, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def update_job(job_id, job_details: dict, access_token):
    print('trying3')
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.put(constants.BASE_URL + f'/job_opening/update-job/{job_id}', json=job_details, headers=headers)
        print(response.status_code)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_job(job_id: int):
    try:
        response = requests.get(constants.BASE_URL + f'/jobs/{job_id}')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")


def get_job_by_username_slug(job_ownername, slug):
    try:
        response = requests.get(constants.BASE_URL + f'/job_openings/{job_ownername}/{slug}')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")


def get_job_by_company_subdomain_slug(company_subdomain, slug, access_token=None):
    try:
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        response = requests.get(
            constants.BASE_URL + f'/job_openings/by-company_subdomain/{company_subdomain}/{slug}',
            headers=headers
        )

        if response.status_code == 200:
            return response.json()

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")

    return None  # Return None if the request fails


def get_user_job_opening_by_username(username: str):
    try:
        response = requests.get(constants.BASE_URL + f'/user-job-openings/{username}')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")

def get_job_opening_by_company_subdomain(company_subdomain: str):
    try:
        response = requests.get(constants.BASE_URL + f'/job-openings/by-company-subdomain/{company_subdomain}')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")


def get_subcategories_by_category(category_id):
    try:
        response = requests.get(constants.BASE_URL + f'/categories/{category_id}/subcategories/')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")


def get_all_categories():
    try:
        response = requests.get(constants.BASE_URL + '/categories/')
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result
        else:
            print("API Error:", response.text)  # Debug: Print error message from API
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def add_category(category, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        "category": category,
    }

    try:
        response = requests.post(constants.BASE_URL + f'/create_category', json=params, headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def update_category(category_id, category, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        "category": category,
    }

    try:
        response = requests.put(constants.BASE_URL + f'/category/update-category/{category_id}', json=params,
                                headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_cms_all_categories(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + '/cms-all-categories', headers=headers)
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result
        else:
            print("API Error:", response.text)  # Debug: Print error message from API
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")




def add_subcategory(subcategory, category_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        "subcategory": subcategory,
        "category_id": category_id
    }

    try:
        response = requests.post(constants.BASE_URL + '/user/create_subcategory', json=params, headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def update_subcategory(subcategory_id, subcategory, category_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        "subcategory": subcategory,
        "category_id": category_id
    }

    try:
        response = requests.put(constants.BASE_URL + f'/user/update_subcategory/{subcategory_id}', json=params,
                                headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()  # Return the response as JSON
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def cms_delete_subcategory(subcategory_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.delete(constants.BASE_URL + f'/cms/delete_subcategory/{subcategory_id}', headers=headers)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_category_name(category_id):
    try:
        response = requests.delete(constants.BASE_URL + f'/category/{category_id}')
        return response.json
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_user_all_tags(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + '/user-tags/', headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print("API Error:", response.text)  # Debug: Print error message from API
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def add_tag(tag, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        "tag": tag,
    }

    try:
        response = requests.post(constants.BASE_URL + f'/tags/', json=params, headers=headers)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def edit_tag(tag_id, new_tag, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
      "new_tag_details": {
        "tag": new_tag
      }
    }

    try:
        response = requests.put(constants.BASE_URL + f'/tags/update/{tag_id}', json=params, headers=headers)

        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def delete_tag(tag_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.delete(constants.BASE_URL + f'/tags/{tag_id}', headers=headers)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_all_email_templates(access_token):
    print("trying")
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        print("try")
        response = requests.get(constants.BASE_URL + '/email-templates/all', headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_subcategory_name(subcategory_id):
    try:
        response = requests.delete(constants.BASE_URL + f'/subcategory/{subcategory_id}')
        return response.json
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def create_template(name, subject, body, access_token):
    print('trying3')
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        "name": name,
        "subject": subject,
        "body": body
    }
    try:
        response = requests.post(constants.BASE_URL + f'/email-templates/create-template', json=params, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:

        print(f"An unexpected error occurred: {err}")

        print(f"An unexpected error occurred: {err}")


def edit_eamil_template(access_token: str, name, subject, body, template_id):
    print("trying")
    headers = {'Authorization': f'Bearer {access_token}'}

    data = {
        "name": name,
        "subject": subject,
        "body": body
    }

    try:
        print("try")
        response = requests.put(constants.BASE_URL + f'/email-templates/update-template/{template_id}', headers=headers,
                                json=data)
        if response.status_code == 200:
            result = response.json()
            return result
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_email_template_by_id(access_token, template_id):
    print("trying")
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        print("try")
        response = requests.get(constants.BASE_URL + f'/email-templates/{template_id}', headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def delete_template(access_token, template_id):
    print("trying")
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        print("try")
        response = requests.delete(constants.BASE_URL + f'/email-templates/delete-template/{template_id}',
                                   headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def send_email(access_token: str, to, subject, body):
    print("trying")
    headers = {'Authorization': f'Bearer {access_token}'}

    data = {
        "to": to,
        "subject": subject,
        "body": body
    }

    try:
        print("try")
        response = requests.post(constants.BASE_URL + f'/email-templates/send-mail', headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            return result
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def is_service_access_allowed(access_token):
    print("trying")
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        print("try")
        response = requests.get(constants.BASE_URL + "/subscriptions/is-service-allowed", headers=headers)
        if response.status_code == 200:
            is_allowed = response.json()
            print('IS ALLOWED TO POST JOB')
            return is_allowed
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")



def upload_medias(file_list, access_token):
    print(file_list)
    print('Trying to upload medias')

    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.post(constants.BASE_URL + f"/upload-multiple-files/", files=file_list, headers=headers)

        print('Response status code:', response.status_code)
        print('Response text:', response.text)

        if response.status_code == 200:
            print('Media uploaded successfully.')
        else:
            print('Failed to upload media.')
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def jobseeker_delete_media(access_token: str, media_id: int):
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.delete(constants.BASE_URL + f'/delete-media/{media_id}', headers=headers)
        print(response.text)
        if response.status_code ==200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")



def subscribe_to_newsletter(name, email, username):
    print("inside api call")

    data = {
      "subscriber_name": name,
      "subscriber_email": email,
      "username":username
    }
    print(data)

    try:
        print('trying to send')
        response = requests.post(constants.BASE_URL + '/newsletter/subscribe_newsletter', json=data)
        print(response.status_code)
        if response.status_code == 200:
            print("successful")
            return response.status_code
        elif response.status_code == 409:
            return response.status_code

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")



def get_user_all_medias(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + '/jobseeker-all-files', headers=headers)
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result
        else:
            print("API Error:", response.text)  # Debug: Print error message from API
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_all_newsletter_subscribers(access_token):
    print("trying")
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        print("try")
        response = requests.get(constants.BASE_URL + '/newsletter/newsletter-subscribers-for-user', headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result


    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_all_user_feedbacks(access_token):
    print("trying")
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        print("try")
        response = requests.get(constants.BASE_URL + '/user/all-feedbacks', headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result


    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_post_by_category_id(author_name, category_id):

    try:
        print("try")
        response = requests.get(constants.BASE_URL + f'/posts/by-category-and-author-name/{category_id}/{author_name}')
        if response.status_code == 200:
            return response.json()

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_post_by_tags(tag_id, username):
    try:
        print("try")
        response = requests.get(constants.BASE_URL + f'/posts/by-tag-and-username/{username}/{tag_id}')
        if response.status_code == 200:
            return response.json()

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")



def send_newsletter(access_token: str, subject, body, post_url):
    print("Trying to send newsletter...")
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {
        "to": 'subscribers',
        "subject": subject,
        "body": body
    }
    url = constants.BASE_URL + f'/newsletter/send-newsletter?post_url={post_url}'

    try:
        print("Sending request...")
        response = requests.post(url, headers=headers, json=data)
        print(f"Response Status Code: {response.status_code}")
        print(f"Response JSON: {response.json()}")
        if response.status_code == 200:
            result = response.json()
            print("Newsletter sent successfully.")
            return result
        else:
            print(f"Failed to send newsletter. Status Code: {response.status_code}. Message: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")


def unsubscribe_newsletter(email, username):
    data = {
        "subscriber_email": email,
        "username": username,
    }

    try:
        print("try")
        response = requests.post(constants.BASE_URL + '/newsletter/unsubscribe-newsletter', json=data)
        if response.status_code == 200:
            result = response.json()
            return result
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")



def get_a_post_all_comments(post_id):
    try:
        response = requests.get(constants.BASE_URL + f'/comment/by_post_id/{post_id}')
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result
        else:
            print("API Error:", response.text)  # Debug: Print error message from API
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_all_comments(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + f'/comment/all', headers=headers)
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result
        else:
            print("API Error:", response.text)  # Debug: Print error message from API
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")

def add_comment(reply_id, post_id, comment, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        "post_id": post_id,
        "reply_id": reply_id,
        "comment": comment
    }

    try:
        response = requests.post(constants.BASE_URL + f'/post/add_comment', json=params, headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def delete_comment(comment_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.delete(constants.BASE_URL + f'/posts/delete-comment/{comment_id}', headers=headers)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")

def add_like_to_comment(post_id, comment_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        "post_id": post_id,
        "comment_id": comment_id
    }
    print("le bhai")
    try:
        response = requests.post(constants.BASE_URL + f'/user/add_like_to_a_comment', json=params, headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")

def remove_like_from_comment(comment_like_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    print("le bhai")
    try:
        response = requests.delete(constants.BASE_URL + f'/comments/remove-like/{comment_like_id}', headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def activate_comments(comment_id):

    try:
        response = requests.post(constants.BASE_URL + f'/comment/toggle_status/{comment_id}')
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result
        else:
            print("API Error:", response.text)  # Debug: Print error message from API
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def deactivate_comments(comment_id):

    try:
        response = requests.post(constants.BASE_URL + f'/comment/deactivate/{comment_id}')
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result
        else:
            print("API Error:", response.text)  # Debug: Print error message from API
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def save_comment_settings(settings, access_token):
    print("save comment")
    print(settings)
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        "notify_linked_blogs": settings.get('notify_linked_blogs', False),
        "allow_trackbacks": settings.get('allow_trackbacks', False),
        "allow_comments": settings.get('allow_comments', False),
        "comment_author_info": settings.get('comment_author_info', False),
        "registered_users_comment": settings.get('registered_users_comment', False),
        "auto_close_comments": settings.get('auto_close_comments', 14),
        "show_comment_cookies": settings.get('show_comment_cookies', False),
        "enable_threaded_comments": settings.get('enable_threaded_comments', False),
        "email_new_comment": settings.get('email_new_comment', False),
        "email_held_moderation": settings.get('email_held_moderation', False),
        "email_new_subscription": settings.get('email_new_subscription', False),
        "comment_approval": settings.get('comment_approval', 'manual')
    }

    try:
        response = requests.post(constants.BASE_URL + '/settings/update_comment_settings', json=params, headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")



def get_comments_settings(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + f'/settings/get_comment_settings', headers=headers)
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result
        else:
            print("API Error:", response.text)  # Debug: Print error message from API
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_like_of_a_comment(post_id):
    print(post_id)
    try:
        response = requests.get(constants.BASE_URL + f'/comment/like/{post_id}')
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result
        else:
            print("API Error:", response.text)  # Debug: Print error message from API
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def user_contact_form(username, firstname, lastname, email, message):
    print("api trying")
    data = {
        "username": username,
        "firstname": firstname,
        "lastname": lastname,
        "email": email,
        "message": message
    }

    try:
        response = requests.post(constants.BASE_URL + '/user-contact-form', json=data)
        print(response.text)
        if response.status_code == 200:

            return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_stats(access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + '/user/stats', headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


############################ PAGES ######################################
def create_page(title, content, status, access_token):
    print('trying to create page')
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {
        "title": title,
        "content": content,
        "status": status
    }
    try:
        response = requests.post(constants.BASE_URL + '/page/create-page', json=data, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def update_page(page_id, title, content, status, access_token):
    print('API CALL: Update Page')
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
          "title": title,
          "content": content,
          "status": status
        }

    try:
        response = requests.put(constants.BASE_URL + f'/page/update-page/{page_id}', json=params, headers=headers)
        print(response.status_code)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_page(page_id: int):
    try:
        response = requests.get(constants.BASE_URL + f'/page/{page_id}')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")


def get_page_by_username_slug(page_ownername, page_slug):
    try:
        response = requests.get(constants.BASE_URL + f'/page/{page_ownername}/{page_slug}')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")


def get_user_all_pages(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + f'/page/user-all-pages', headers=headers)
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print("API Error:", response.text)  # Debug: Print error message from API
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def delete_page(page_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.delete(constants.BASE_URL + f'/page/delete-page/{page_id}', headers=headers)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_user_from_google_login(user_info):

    try:
        response = requests.get(constants.BASE_URL + '/get-google-user-info', json=user_info)
        print("Response Status Code:", response.status_code)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print("API Error:", response.text)  # Debug: Print error message from API
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")

#################################### FORM BUILDER ##############################################################


def create_form(form_name, form_unique_id, form_html, access_token):
    print('trying to create form')
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {
        "form_name": form_name,
        "unique_id": form_unique_id,
        "form_html": form_html
    }
    try:
        response = requests.post(constants.BASE_URL + '/formbuilder/create-form', json=data, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_user_all_forms(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + f'/formbuilder/user-all-forms', headers=headers)
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print("API Error:", response.text)  # Debug: Print error message from API
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_form_by_unique_id(form_id: str):
    try:
        response = requests.get(constants.BASE_URL + f'/formbuilder/forms/{form_id}')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")


def collect_form_response(unique_id, response_data):
    print('trying to send response')
    data = {
        "response_data": response_data
           }
    try:
        response = requests.post(constants.BASE_URL + f'/formbuilder/{unique_id}/add-response', json=data)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def delete_form_by_unique_id(form_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.delete(constants.BASE_URL + f'/formbuilder/delete-user-form/{form_id}', headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


############################################## RESUME PARSER #######################################################

def add_new_resume_collection(resumes, access_token):
    print('trying to add resume collection')
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {
        "json_data": resumes
    }

    try:
        response = requests.post(constants.BASE_URL + '/resume_parser_v2/add-resume', json=data, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_past_resume_records(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + '/resume_parser_v2/resumes-history', headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


##################################################### CHATBOT ##############################################################################

def chatbot_save_chat(messages, access_token):
    print('trying to save chat')
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {
        "json_data": messages
    }

    try:
        response = requests.post(constants.BASE_URL + '/chatbot/save-chat', json=data, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_user_all_chats(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + '/chatbot/all-chats', headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_all_security_groups(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + '/access-management/all-groups', headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def create_security_group(access_token, permissions, group_name):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        "name": group_name
    }
    data = {
        "permission_names": permissions
    }
    pprint.pprint(data)

    try:
        response = requests.post(constants.BASE_URL + f'/access-management/groups/create-group', params=params, json=data, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def delete_security_groups(access_token, group_id):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.delete(constants.BASE_URL + f'/access-management/groups/delete-group/{group_id}', headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_security_group(access_token, group_id):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + f'/access-management/groups/{group_id}', headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def update_security_group(access_token, permissions, group_name, group_id):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        "name": group_name
    }
    data = {
        "permission_names": permissions
    }
    pprint.pprint(data)

    try:
        response = requests.put(constants.BASE_URL + f'/access-management/groups/update-group/{group_id}', params=params, json=data, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def jobseeker_login(email, password):
    print('trying2')
    data = {
        "username": email,
        "password": password
    }

    try:
        response = requests.post(constants.BASE_URL + '/jobseeker-login', data=data)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def jobseeker_register(firstname,lastname,phone_number, email, password):
    print('trying3')
    headers = {'Content-Type': 'application/json'}
    data = {
        "firstname": firstname,
        "lastname": lastname,
        "phone_number": phone_number,
        "email": email,
        "password": password,
        "role": "user",
    }

    try:
        response = requests.post(constants.BASE_URL + f'/jobseeker-register', data=json.dumps(data), headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def apply_to_job_via_resume_list(access_token, job_id):
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.post(constants.BASE_URL + f'/jobs/{job_id}/apply', headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def apply_to_job_via_device(access_token, job_id, file):
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.post(constants.BASE_URL + f'/jobs/{job_id}/apply', files=file, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_jobseeker_applications(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + f'/applicants/my-applications', headers=headers)
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result

        else:
            print("API Error:", response.text)
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def update_application_status(application_id, new_status, stage_id, stage_name):
    try:
        data = {
            "id": application_id,
            "new_status": new_status,
            "stage_id": stage_id,
            "stage_name": stage_name
        }
        response = requests.post(constants.BASE_URL + f'/update-job-application-status', json=data)
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result

        else:
            print("API Error:", response.text)
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")

def get_board_columns(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + f'/get-job-application-board-columns', headers=headers)
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result

        else:
            print("API Error:", response.text)
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_applicant_trackers(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + f'/get-job-application-board-columns', headers=headers)
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result

        else:
            print("API Error:", response.text)
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def create_application_tracker(stage_type, stage_number, name, description, job_status, access_token):
    print("inside api call")
    headers = {'Authorization': f'Bearer {access_token}'}

    data = {
        "name": name,
        "description": description,
        "job_status": job_status,
        "stage_type": stage_type,
        "stage_order": stage_number
    }

    try:
        response = requests.post(constants.BASE_URL + '/create-job-application-board-column', json=data, headers=headers)
        if response.status_code == 200:
            print("successful")
            return response.json
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def delete_application_tracker(tracker_id, access_token):
    print("inside api call")
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.delete(constants.BASE_URL + f'/delete-job-application-board-column/{tracker_id}', headers=headers)
        if response.status_code == 200:
            print("successful")
            return response.json
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")



def get_jobseeker_profile(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.get(constants.BASE_URL + '/jobseeker/get-jobseeker-profile', headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def employer_view_jobseeker(jobseeker_id):
    # headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.get(constants.BASE_URL + f'/get-jobseeker-profile-for-employer/{jobseeker_id}')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")



def add_about_profile(content, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {
        "content": content
    }

    try:
        response = requests.post(constants.BASE_URL + '/jobseeker/profile_summaries/create-profile-summary',json=data, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def add_education_profile(education, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.post(constants.BASE_URL + '/jobseeker/educations/create-education',json=education, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def add_experience_profile(experience, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}


    try:
        response = requests.post(constants.BASE_URL + '/jobseeker/experiences/create-experience',json=experience, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def add_internships_profile(internships, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}


    try:
        response = requests.post(constants.BASE_URL + '/jobseeker/internships/create-internship', json=internships, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def add_projects_profile(projects, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}


    try:
        response = requests.post(constants.BASE_URL + '/jobseeker/projects/create-project',json=projects, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")

def add_accomplishments_profile(accomplishments, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.post(constants.BASE_URL + '/jobseeker/accomplishments/create-accomplishment', json=accomplishments, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def update_basic_info(access_token, firstname=None, lastname=None, email=None, phone_number=None, profile_picture=None):
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {}

    if firstname:
        print(firstname)
        data['firstname'] = firstname
    if lastname:
        print(lastname)
        data['lastname'] = lastname

    if email:
        data['email'] = email
        print(email)

    if phone_number:
        data['phone_number'] = phone_number
        print(phone_number)


    try:
        print(data)
        response = requests.put(constants.BASE_URL + '/jobseeker/update-basic-info', params=data, files=profile_picture if profile_picture else None, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def delete_jobseeker_profile_info(access_token,type, id):
    headers = {'Authorization': f'Bearer {access_token}'}
    if type == 'profile_summary':
        url=constants.BASE_URL+f'/jobseeker/profile_summaries/delete-profile-summary/{id}'
    elif type == 'education':
        url=constants.BASE_URL+f'/jobseeker/educations/delete-education/{id}'
    elif type == 'experience':
        url=constants.BASE_URL+f'/jobseeker/experiences/delete-experience/{id}'
    elif type == 'internship':
        url=constants.BASE_URL+f'/jobseeker/internships/delete-internship/{id}'
    elif type == 'project':
        url=constants.BASE_URL+f'/jobseeker/projects/delete-project/{id}'
    elif type == 'accomplishment':
        url=constants.BASE_URL+f'/jobseeker/accomplishments/delete-accomplishment/{id}'



    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_jobseeker_stats(access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + '/jobseeker/stats', headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_jobseeker_recommendations(jobs_count, access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + f'/jobseeker/recommendations/{jobs_count}', headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_filtered_jobs(access_token:str = None, country:str = None, state:str = None, job_type:str = None, industry:str = None, date_filter:str = None, keyword:str = None, skip:int = 0, limit:int=10):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        'keyword': keyword,
        'address_country': country,
        'address_province': state,
        'job_type': job_type,
        'industry': industry,
        'date_filter': date_filter,
        'skip':skip,
        'limit':limit
    }
    try:
        response = requests.get(constants.BASE_URL + f'/jobs/filter/', params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_filtered_applicants(params):
    try:
        response = requests.get(constants.BASE_URL + f'/applicants/filter', params=params)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")



def get_filtered_applicants_for_employer(params, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.get(constants.BASE_URL + f'/employer/applicants/filter', params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_filtered_jobseekers(jobseeker_id=None, name=None, email=None, phone_no=None):
    print('inside filter jobseeker api call')
    params = {
        'jobseeker_id': jobseeker_id,
        'name': name,
        'email': email,
        'phone_number': phone_no
    }
    try:
        response = requests.get(constants.BASE_URL + f'/jobseeker/filter/', params=params)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_admin_stats():
    print('inside admin_stats api call')
    try:
        response = requests.get(constants.BASE_URL + f'/admin/stats')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_employer_reports(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}

    print('inside admin_stats api call')
    try:
        response = requests.get(constants.BASE_URL + f'/employer/reports', headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def update_jobseeker_profile(profile_data, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.post(constants.BASE_URL + '/jobseeker/create-jobseeker-profile',json=profile_data, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")

def update_jobseeker_profile_two(profile_data, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.post(constants.BASE_URL + '/jobseeker/update-jobseeker-profile', json=profile_data, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def homepage_contact_form_submission(name, email, message):
    data = {
        'name': name,
        'email': email,
        'message': message
    }

    try:
        response = requests.post(constants.BASE_URL + '/homepage_contact_form_submission', json=data)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_all_posts():
    try:
        response = requests.get(constants.BASE_URL + '/all-posts/')
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result
        else:
            print("API Error:", response.text)  # Debug: Print error message from API
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_admin_all_posts(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + f'/admin-all-posts', headers=headers)
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result

        else:
            print("API Error:", response.text)
            abort(response.status_code)
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def admin_delete_post(post_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.delete(constants.BASE_URL + f'/posts/delete-post/{post_id}', headers=headers)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def create_post(title, short_description, featured_image, content, category_id, subcategory_id, status, access_token, tags, send_newsletter):
    print('Trying to create post')

    headers = {'Authorization': f'Bearer {access_token}'}

    # Correctly format the post data as JSON
    post_data = {
        "title": title,
        "short_description": short_description,
        "content": content,
        "category_id": category_id,
        "subcategory_id": subcategory_id,
        "status": status,  # This is already a list
        "send_newsletter": send_newsletter
    }
    print(post_data)


    post_data["tags"] = json.dumps(tags)  # <-- FastAPI will need to parse this
   

    files = {}
    if featured_image:
        files["featured_image"] = ("featured.jpg", featured_image, "image/jpeg")  # or detect mime-type

    print(post_data)

    try:
        response = requests.post(
            constants.BASE_URL + "/posts/create-post",
            data=post_data,  # Send post as form-data
            files=files,  # Attach image
            headers=headers
        )

        # Debugging response
        print(response.status_code, response.text)

        if response.status_code == 200:
            return response.json()
        else:
            return response.text  # Return error details if not 200 OK
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def admin_update_post(post_id, title, content, category_id, subcategory_id, status, access_token, tags, short_description, featured_image=None):
    print('trying3')
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
          "title": title,
          "content": content,
          "category_id": category_id,
          "subcategory_id": subcategory_id,
          "status": status,
          "tags":tags,
          "short_description": short_description
        }
    
    params["tags"] = json.dumps(tags)  # <-- FastAPI will need to parse this
   

    files = {}
    if featured_image:
        files["featured_image"] = ("featured.jpg", featured_image, "image/jpeg")  # or detect mime-type


    try:
        response = requests.put(constants.BASE_URL + f'/posts/update-post/{post_id}', data=params, files=files, headers=headers)
        print(response.status_code)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_post(post_id: int):
    try:
        response = requests.get(constants.BASE_URL + f'/posts/get-post/{post_id}')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")


def get_post_by_slug(slug):
    try:
        response = requests.get(constants.BASE_URL + f'/posts/{slug}')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")


def get_subcategories_by_category(category_id):
    try:
        response = requests.get(constants.BASE_URL + f'/categories/{category_id}/subcategories/')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")


def get_all_categories():
    try:
        response = requests.get(constants.BASE_URL + '/categories/')
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result
        else:
            print("API Error:", response.text)  # Debug: Print error message from API
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def add_category(category, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        "category": category,
    }

    try:
        response = requests.post(constants.BASE_URL + f'/create_category', json=params, headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def update_category(category_id, category, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        "category": category,
    }

    try:
        response = requests.put(constants.BASE_URL + f'/category/update-category/{category_id}', json=params,
                                headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_cms_all_categories(access_token):
    try:
        response = requests.get(constants.BASE_URL + '/cms-all-categories')
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)  # Debug: Print API result
            return result
        else:
            print("API Error:", response.text)  # Debug: Print error message from API
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def cms_delete_category(category_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.delete(constants.BASE_URL + f'/category/delete-category/{category_id}', headers=headers)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def add_subcategory(subcategory, category_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        "subcategory": subcategory,
        "category_id": category_id
    }

    try:
        response = requests.post(constants.BASE_URL + '/cms/create_subcategory', json=params, headers=headers)
        print(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def update_subcategory(subcategory_id, subcategory, category_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        "subcategory": subcategory,
        "category_id": category_id
    }

    try:
        response = requests.put(constants.BASE_URL + f'/cms/update_subcategory/{subcategory_id}', json=params,
                                headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()  # Return the response as JSON
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def delete_subcategory(subcategory_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.delete(constants.BASE_URL + f'/cms/delete_subcategory/{subcategory_id}', headers=headers)
        return response
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def get_category_name(category_id):
    try:
        response = requests.delete(constants.BASE_URL + f'/category/{category_id}')
        return response.json
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")

def get_post_by_category(category):
    try:
        response = requests.get(constants.BASE_URL + f'/posts/by-category-name/{category}')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")

def get_post_by_subcategory(subcategory):
    try:
        response = requests.get(constants.BASE_URL + f'/posts/by-subcategory-name/{subcategory}')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")


def get_post_by_tag(tag):
    try:
        response = requests.get(constants.BASE_URL + f'/posts/by-tag/{tag}')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")


############################################## ADMIN DASHBOARD ###################################################

def get_admin_stats_for_dashboard(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(constants.BASE_URL + '/admin/stats_for_admin', headers=headers)
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            print(result)
            return result
        else:
            print("API Error:", response.text)  # Debug: Print error message from API
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")

############################################# GET SITEMAP DATA ##################################################

def get_sitemap_data():
    try:
        response = requests.get(constants.BASE_URL + f'/admin/sitemap-data')
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            return result

        else:
            print("API Error:", response.text)
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def subscribe_newsletter(email):
    try:
        data = {
            "email": email
        }
        response = requests.post(constants.BASE_URL + f'/admin/newsletter/subscribe', json=data)
        print("Response Status Code:", response.status_code)  # Debug: Print status code
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print("API Error:", response.text)
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")



def add_team_members(access_token, members):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(constants.BASE_URL + '/team/create', json=members, headers=headers)
        print("Response Status Code:", response.status_code)
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)
            return result
        else:
            print("API Error:", response.text)
    except requests.exceptions.RequestException as err:
        print(f"Request error: {err}")

def read_team_members(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.get(constants.BASE_URL + '/team/members', headers=headers)
        print("Response Status Code:", response.status_code)
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)
            return result
        else:
            print("API Error:", response.text)
    except requests.exceptions.RequestException as err:
        print(f"Request error: {err}")


def update_team_members(access_token, user_id, permissions):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.put(constants.BASE_URL + f'/team/update-permissions/{user_id}', json=permissions, headers=headers)
        print("Response Status Code:", response.status_code)
        if response.status_code == 200:
            result = response.json()
            print("API Result:", result)
            return result
        else:
            print("API Error:", response.text)
    except requests.exceptions.RequestException as err:
        print(f"Request error: {err}")


def save_job_for_jobseeker(job_id: int, access_token: str):

    url = constants.BASE_URL + f"/jobseeker/save-job/{job_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to save job: {response.text}")

def unsave_job_for_jobseeker(job_id: int, access_token: str):
    import requests

    url = constants.BASE_URL+f"/jobseeker/unsave-job/{job_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.delete(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to unsave job: {response.text}")


def get_saved_jobs_for_jobseeker(access_token: str):
    import requests

    url = constants.BASE_URL+"/jobseeker/saved-jobs"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get saved jobs: {response.text}")

############################################### APPLICATION LOG ##################################################


def create_application_stage_log(log_data):
    """
    Create a new application stage log.
    :param log_data: dict or Pydantic model with log fields
    :return: dict (created log)
    """
    url = constants.BASE_URL + "/application-log/"
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=log_data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to create application stage log: {response.text}")


def update_application_stage_log(log_id, log_update_data):
    """
    Update an application stage log.
    :param log_id: int, log ID
    :param log_update_data: dict or Pydantic model with update fields
    :return: dict (updated log)
    """
    url = constants.BASE_URL + f"/application-log/{log_id}"
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.put(url, json=log_update_data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to update application stage log: {response.text}")


def get_application_stage_log_by_id(log_id):
    """
    Get a single application stage log by ID.
    :param log_id: int, log ID
    :return: dict (log)
    """
    url = constants.BASE_URL + f"/application-log/{log_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get application stage log by id: {response.text}")


def get_application_stage_logs_by_application(job_application_id):
    """
    Get all logs for a job application.
    :param job_application_id: int, job application ID
    :return: list of dicts (logs)
    """
    url = constants.BASE_URL + f"/application-log/by-application/{job_application_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get logs by application: {response.text}")


def get_application_stage_log_by_application_and_stage(job_application_id, stage_id):
    """
    Get a single application stage log by job_application_id and stage_id.
    :param job_application_id: int, job application ID
    :param stage_id: int, stage ID
    :return: dict (log)
    """
    url = constants.BASE_URL + "/application-log/by-application-and-stage/"
    params = {
        "job_application_id": job_application_id,
        "stage_id": stage_id
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get application stage log by application and stage: {response.text}")

def get_user_preferences(access_token):
    """
    Calls the API to get the current user's preferences.
    :param access_token: str, user's access token
    :return: dict (user preferences)
    """
    headers = {'Authorization': f'Bearer {access_token}'}
    url = constants.BASE_URL + "/employer/preferences/"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def update_user_preferences(access_token, preferences_update):
    """
    Calls the API to update the current user's preferences.
    :param access_token: str, user's access token
    :param preferences_update: dict, fields to update (e.g., {"email_notifications": True, ...})
    :return: dict (updated user preferences)
    """
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    url = constants.BASE_URL + "/employer/preferences/update"
    response = requests.put(url, headers=headers, json=preferences_update)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to update user preferences: {response.text}")
