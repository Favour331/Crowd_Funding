from models.backings import fetch_user_by_id, add_new_backing

def create_backing(user_id, project_id, amount, email):
    """Service function to create a new backing"""
    if not user_id or not project_id or not amount or not email:
        return None  # Invalid input

    add_new_backing(user_id, project_id, amount, email)
    return True

def get_backings_for_project(project_id):
    """Service function to fetch backings for a specific project"""
    if not project_id:
        return None  # Invalid input
    
    backings = fetch_backings_by_project(project_id)
    return backings

def fetch_user_profile(user_id):
    """Service function to fetch user profile data"""
    if not user_id:
        return None  # Invalid input
    
    user = fetch_user_by_id(user_id)
    return user