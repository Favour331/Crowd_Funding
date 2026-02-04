import mysql.connector

def create_updates_table():
    conn = mysql.connector.connect(host='localhost', user='root', passwd='', database='crowd_funding')
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS `updates` (id INT PRIMARY KEY AUTO_INCREMENT,project_id INT NOT NULL,title TEXT NOT NULL,content TEXT NOT NULL,time_and_date DATETIME NOT NULL,CONSTRAINT fk_updates_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    conn.commit()
    cur.close()
    conn.close()

# Optionally call create_updates_table() from your app startup code (not at import time)