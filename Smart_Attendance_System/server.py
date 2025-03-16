from fastapi import FastAPI
import mysql.connector
from database_setup import connect_db

app = FastAPI()

@app.get("/students")
def get_students():
    """Fetch all registered students."""
    conn = connect_db()
    if not conn:
        return {"error": "Database connection failed"}
    
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM students")
    students = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return {"students": students}

@app.get("/attendance")
def get_attendance():
    """Fetch attendance records."""
    conn = connect_db()
    if not conn:
        return {"error": "Database connection failed"}
    
    cursor = conn.cursor()
    cursor.execute("SELECT students.name, attendance.timestamp FROM attendance JOIN students ON attendance.student_id = students.id")
    attendance_records = [{"name": row[0], "timestamp": row[1]} for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return {"attendance": attendance_records}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
