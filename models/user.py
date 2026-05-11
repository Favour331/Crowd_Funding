from db.connection import get_db

def create_user(first, last, email, hashed, role):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""INSERT INTO users (First_name, Last_name, Email, Password, Role)VALUES (%s,%s,%s,%s,%s)""",(first, last, email, hashed, role))
    conn.commit()
    # fetch inserted user
    cur.execute("SELECT * FROM users WHERE Email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def update_profile_image(user_id, profile_image_url):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "UPDATE users SET profile_image_url = %s WHERE id = %s",
        (profile_image_url, user_id)
    )
    conn.commit()
    cur.close()
    conn.close()


def get_user_by_email(email):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT users.*,COUNT(projects.id) AS projects,COALESCE(SUM(projects.backer_count),0) AS backers,COALESCE(SUM(projects.amount_raised),0) AS amount FROM users LEFT JOIN projects ON users.id = projects.creator_id WHERE users.email = %s GROUP BY users.id;", (email,))
        user = cur.fetchone()
    except Exception as e:
        print(f"Error fetching user by email: {e}")
        user = None
    finally:
        cur.close()
        conn.close()
    return user

def go_home_by_id(user_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT users.*,COUNT(projects.id) AS projects,COALESCE(SUM(projects.backer_count),0) AS backers,COALESCE(SUM(projects.amount_raised),0) AS amount FROM users LEFT JOIN projects ON users.id = projects.creator_id WHERE users.id = %s GROUP BY users.id;", (user_id,))
        user = cur.fetchone()
    except Exception as e:
        print(f"Error fetching user by ID: {e}")
        user = None
    finally:
        cur.close()
        conn.close()
    return user

def fetch_user_details(user_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE Id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row
    
def get_user_profile(user_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    # Fetch user once
    cur.execute("""SELECT * FROM users WHERE users.id = %s""", (user_id,))
    user = cur.fetchone()
    return user

def get_user_projects_by_user_id(user_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    # Fetch user once
    cur.execute("""SELECT p.*,COUNT(b.Id) AS total_backers,COALESCE(SUM(b.Amount), 0) AS total_pledged FROM projects p LEFT JOIN backings b ON p.Id = b.Project_Id WHERE p.creator_id = %s GROUP BY p.Id""", (user_id,))
    user = cur.fetchall()
    return user
def get_search_results(query):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""SELECT 'project' AS type,p.Id,p.Title AS name,p.Description,p.main_image_url AS image,u.Last_name AS creator_name,NULL AS Role FROM projects p JOIN users u ON p.creator_id = u.Id WHERE p.Title LIKE %s OR CAST(p.Id AS CHAR) LIKE %s
    UNION ALL
    SELECT 'user' AS type,u.Id,CONCAT(u.Last_name, ' ', u.First_name) AS name,NULL AS Description,u.profile_image_url AS image,NULL AS creator_name,u.Role FROM users u WHERE u.First_name LIKE %s OR u.Last_name LIKE %s""", (f'%{query}%',f'%{query}%',f'%{query}%',f'%{query}%'))

    results = cur.fetchall()
    return results