from models.projects import fetch_user_projects, fetch_user_by_id,fetch_each_project,fetch_all_projects

def get_dashboard_data(user_id):
    """
    Returns complete dashboard data for a user:
    - User profile info
    - Projects list with stats
    - Aggregated counts by status
    """
    if not user_id:
        return None
        
    # Get user info
    user = fetch_user_by_id(user_id)
    if not user:
        return None
    
    # Get projects with stats
    projects = fetch_user_projects(user_id)
    
    # Calculate aggregated stats
    stats = {
        'active': sum(1 for p in projects if p['status'] == 'active'),
        'pending': sum(1 for p in projects if p['status'] == 'pending_review'),
        'rejected': sum(1 for p in projects if p['status'] == 'rejected'),
        'total': len(projects)
    }
    
    return {
        'user': user,
        'projects': projects,
        'stats': stats,
        'role': user.get('Role', 'guest').lower()
    }
    
def get_each_projects(project_id):
    """
    Fetches details for a specific project.
    """
    project = fetch_each_project(project_id)
    if not project:
        return None
    
    return project

def get_all_projects():
    """
    Fetches all projects with aggregated data.
    """
    projects = fetch_all_projects()
    if not projects:
        return []
    
    return projects