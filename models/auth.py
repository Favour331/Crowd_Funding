from db.connection import get_db

def create_user(username, first, last, email, hashed, role):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """INSERT INTO users 
        (username, First_name, Last_name, Email, Password, Role)
        VALUES (%s,%s,%s,%s,%s,%s)""",
        (username, first, last, email, hashed, role)
    )
    conn.commit()
    # fetch inserted user
    cur.execute("SELECT * FROM users WHERE Email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user
