import mysql.connector

# Database connection details
DB_HOST = "localhost"
DB_USER = "Smart_Attendance_Admin"
DB_PASSWORD = "Smart_MEC"
DB_NAME = "attendance_db"

def connect_db():
    """Establish a database connection."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except mysql.connector.Error as e:
        print("Error connecting to database:", e)
        return None

def create_tables():
    """Ensure necessary tables exist."""
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            face_encoding TEXT NOT NULL
        )""")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )""")
        
        conn.commit()
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_tables()
    print("✅ Database and tables are set up!")
