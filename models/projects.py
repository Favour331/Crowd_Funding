import mysql.connector
from mysql.connector import Error

def create_projects_table():
    conn = None
    cur = None
    try:
        conn = mysql.connector.connect(host='localhost', user='root', passwd='', database='crowd_funding')
        project = conn.cursor()
        project.execute("""
        CREATE TABLE IF NOT EXISTS projects (id INT PRIMARY KEY AUTO_INCREMENT,creator_id INT NOT NULL,title VARCHAR(255) UNIQUE NOT NULL,slug VARCHAR(300) NOT NULL,description TEXT NOT NULL,short_desc VARCHAR(500),category ENUM('tech','art','design','food','games','music','publishing','film','fashion','other') NOT NULL,funding_goal DECIMAL(15,2) NOT NULL,amount_raised DECIMAL(15,2) DEFAULT 0.00,currency VARCHAR(3) DEFAULT 'USD',main_image_url VARCHAR(500),video_url VARCHAR(500),gallery_images JSON,story LONGTEXT,risk_challenges TEXT,rewards JSON,deadline DATE NOT NULL,status ENUM('pending_review','draft','active','successful','failed','cancelled') DEFAULT 'draft',is_featured TINYINT(1) DEFAULT 0,approved_at DATETIME NULL,approved_by INT NULL,rejection_reason TEXT,backer_count INT DEFAULT 0,view_count INT DEFAULT 0,created_at DATETIME DEFAULT CURRENT_TIMESTAMP,updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,launched_at DATETIME NULL,completed_at DATETIME NULL,CONSTRAINT fk_projects_creator FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE,CONSTRAINT fk_projects_approved_by FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        conn.commit()
    except Error as e:
        print("Error creating projects table:", e)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# Optionally call create_projects_table() from your app start-up code (not at import time)