import mysql.connector

def create_likes_table():
    conn = mysql.connector.connect(host='localhost', user='root', passwd='', database='crowd_funding')
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS `Comments` (id INT PRIMARY KEY AUTO_INCREMENT,backers_id INT NOT NULL,project_id INT NOT NULL, Comments Text Not Null,time_and_date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL)
    """)
    conn.commit()
    cur.close()
    conn.close()

# Optionally call create_updates_table() from your app startup code (not at import time)