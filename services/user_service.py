import email

from requests import request

from models.user import get_user_by_email,create_user,fetch_user_details,go_home_by_id,update_profile_image,get_user_profile,get_user_projects_by_user_id,get_search_results
from werkzeug.security import check_password_hash,generate_password_hash

def authenticate_user(email, password):
    user = get_user_by_email(email)

    if not user:
        return None

    if not check_password_hash(user["Password"], password):
        return None

    return user


def save_profile_image(user_id, profile_image_url):
    update_profile_image(user_id, profile_image_url)


def get_user_by_id(user_id):
    user = go_home_by_id(user_id)

    if not user:
        return None
    
    return user


def get_user_details(user_id):
    user_details = fetch_user_details(user_id)
    if not user_details:
        return None
    return user_details

def create_one_user(first,last,email,password,role):
    
    hashed = generate_password_hash(password)
    user = create_user(first,last,email,hashed,role)
    if not user:
        return None
    
    return user

def get_user_profile_by_id(user_id):
    user_role = get_user_profile(user_id)
    if not user_role:
        return None
    return user_role

def get_user_profile_and_projects(user_id):
    get_projects = get_user_projects_by_user_id(user_id)
    if get_projects is None:
        return None
    return get_projects

def get_results(query):
    # Implement search logic here, e.g., search in projects and users
    # For demonstration, we'll just return the query
    get_search = get_search_results(query)
    if not get_search:
        return None
    return get_search
