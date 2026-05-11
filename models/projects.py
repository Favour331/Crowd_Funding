import mysql

from db.connection import get_db

def fetch_user_by_id(user_id):
    """Fetch user profile data"""
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT users.*,projects.status as stats,projects.* from users left join projects on users.Id = projects.creator_id WHERE users.Id = %s", (user_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result

def fetch_user_projects(user_id):
    """Fetch projects for a specific user with aggregated data"""
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT p.*,COALESCE(SUM(b.amount), 0) as current_amount,COUNT(DISTINCT b.project_id) as backers_count,DATEDIFF(p.deadline, CURDATE()) as days_remaining FROM projects p LEFT JOIN backings b ON b.project_Id = p.Id WHERE p.creator_id = %s GROUP BY p.Id ORDER BY p.created_at DESC """, (user_id,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

def fetch_all_projects():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""SELECT p.*,COUNT(DISTINCT c.Id) AS comment_count,COUNT(DISTINCT l.Id) AS like_count,u.First_name AS creator_name FROM projects p LEFT JOIN comments c ON c.project_id = p.Id LEFT JOIN likes l ON l.project_id = p.Id LEFT JOIN users u ON u.Id = p.creator_id GROUP BY p.Id""")
    projects = cur.fetchall()
    cur.close()
    conn.close()
    return projects

def fetch_each_project(project_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("Select p.*,u.* From projects p left join users u on u.Id = p.creator_id where p.Id = %s group by p.creator_id",(project_id,))
    row = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return row