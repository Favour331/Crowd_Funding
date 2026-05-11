import mysql.connector

def create_likes_table():
    conn = mysql.connector.connect(host='localhost', user='root', passwd='', database='crowd_funding')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE backings (id INT AUTO_INCREMENT PRIMARY KEY,user_id INT NOT NULL,project_id INT NOT NULL,amount DECIMAL(10,2) NOT NULL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
""")
    conn.commit()
    cur.close()
    conn.close()

# Optionally call create_updates_table() from your app startup code (not at import time)