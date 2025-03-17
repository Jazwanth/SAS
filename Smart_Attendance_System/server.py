from fastapi import FastAPI, HTTPException
from datetime import datetime
import mysql.connector

app = FastAPI()

# ✅ Database Connection with Error Handling
try:
    db = mysql.connector.connect(
        host="localhost",
        user="Smart_Attendance_Admin",
        password="Smart_MEC",
        database="attendance_db"
    )
    cursor = db.cursor()
    print("✅ Connected to MySQL successfully.")
except mysql.connector.Error as err:
    print(f"❌ Error connecting to MySQL: {err}")
    exit(1)  # Exit the app if the database fails to connect

# ✅ API to Fetch Attendance Logs
@app.get("/attendance")
def get_attendance(date: str = None, student_name: str = None):
    query = "SELECT student_name, date, status FROM attendance"
    conditions = []
    params = []

    if date:
        conditions.append("date = %s")
        params.append(date)
    if student_name:
        conditions.append("student_name = %s")
        params.append(student_name)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cursor.execute(query, params)
    records = cursor.fetchall()

    if not records:
        raise HTTPException(status_code=404, detail="No attendance records found.")

    return {"attendance": [{"name": r[0], "date": r[1], "status": r[2]} for r in records]}

# ✅ API to Mark Attendance (Prevent Duplicate Entries)
@app.post("/mark_attendance")
def mark_attendance(student_name: str):
    today_date = datetime.now().strftime('%Y-%m-%d')

    # Check if attendance is already marked
    cursor.execute("SELECT * FROM attendance WHERE student_name = %s AND date = %s", (student_name, today_date))
    existing_record = cursor.fetchone()

    if existing_record:
        return {"message": f"{student_name} is already marked present today."}

    # Mark attendance
    cursor.execute("INSERT INTO attendance (student_name, date, status) VALUES (%s, %s, %s)", (student_name, today_date, "Present"))
    db.commit()
    
    return {"message": f"Attendance marked for {student_name} on {today_date}"}
