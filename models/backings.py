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

def add_new_backing(user_id, project_id, amount, email):
    """Add a new backing to the database"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO backings (user_id, project_id, amount, user_email,created_at) VALUES (%s, %s, %s, %s, NOW())',
                (user_id, project_id, amount, email))
    cur.execute('UPDATE `projects` SET `amount_raised` = `amount_raised` + %s WHERE `projects`.`id` = %s', (amount, project_id))
    cur.execute('UPDATE `projects` SET `backer_count` = `backer_count` + 1 WHERE `projects`.`id` = %s and `projects`.`id` IN (SELECT DISTINCT `project_id` FROM `backings` WHERE `project_id` = %s)', (project_id, project_id))
    conn.commit()
    cur.close()
    conn.close()
        
    """Fetch all backings for a specific project"""
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, creator_id, funding_goal, deadline, status FROM projects WHERE id = %s", (project_id,))
    project = cur.fetchone()
    return project