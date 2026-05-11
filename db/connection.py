import mysql.connector
from config import Config

def initialize_database():
    """Create database and tables if they don't exist"""
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            passwd=Config.DB_PASSWORD
        )
        cur = conn.cursor()
        cur.execute("CREATE DATABASE IF NOT EXISTS {}".format(Config.DB_NAME))
        cur.execute("USE {}".format(Config.DB_NAME))
        
        # Users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                First_name VARCHAR(50),
                Last_name VARCHAR(50),
                Email VARCHAR(100) NOT NULL UNIQUE,
                Password VARCHAR(255) NOT NULL,
                Role ENUM('user', 'Creator', 'Backer', 'admin') DEFAULT 'user',
                profile_image_url VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Ensure existing tables can accept Backer role values
        cur.execute("ALTER TABLE users MODIFY COLUMN Role ENUM('user', 'Creator', 'Backer', 'admin') DEFAULT 'user'")
        
        # Projects table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                creator_id INT NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                funding_goal DECIMAL(12,2) NOT NULL,
                amount_raised DECIMAL(12,2) DEFAULT 0,
                backer_count INT DEFAULT 0,
                status ENUM('active', 'completed', 'cancelled') DEFAULT 'active',
                deadline DATE,
                main_image_url VARCHAR(500),
                category VARCHAR(50),
                risk_challenges TEXT,
                rewards TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Backings table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS backings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                project_id INT NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                user_email VARCHAR(100),
                reference VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        
        # Likes table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS likes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                project_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_like (user_id, project_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        
        # Comments table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                project_id INT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_backings_project ON backings(project_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_backings_user ON backings(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_projects_creator ON projects(creator_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_likes_user ON likes(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_comments_user ON comments(user_id)")
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False

def get_db():
    """Get database connection with auto-initialization"""
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            passwd=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        return conn
    except mysql.connector.Error as err:
        if err.errno == 1049:  # Database doesn't exist
            initialize_database()
            return mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                passwd=Config.DB_PASSWORD,
                database=Config.DB_NAME
            )
        raise
