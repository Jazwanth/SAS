import cv2
import numpy as np
import face_recognition
import mysql.connector
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import uvicorn
import io

# Database connection details
DB_HOST = "localhost"
DB_USER = "Smart_Attendance_Admin"
DB_PASSWORD = "Smart_MEC"
DB_NAME = "attendance_db"

# Connect to MySQL
def connect_db():
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

# Ensure tables exist
def create_tables():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            face_encoding TEXT NOT NULL
        )""")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )""")
        
        conn.commit()
        cursor.close()
        conn.close()

# Register a new student
def register_student(name: str, image_file: UploadFile):
    conn = connect_db()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    image = face_recognition.load_image_file(io.BytesIO(image_file.file.read()))
    face_encodings = face_recognition.face_encodings(image)
    
    if not face_encodings:
        raise HTTPException(status_code=400, detail="No face detected in the image")
    
    face_encoding_str = str(face_encodings[0].tolist())
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, face_encoding) VALUES (%s, %s)", (name, face_encoding_str))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Student registered successfully"}

# Mark attendance
def mark_attendance(student_id: int):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO attendance (student_id) VALUES (%s)", (student_id,))
        conn.commit()
        cursor.close()
        conn.close()

# Face recognition and attendance marking
def recognize_faces():
    known_encodings = load_face_encodings()
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(list(known_encodings.values()), face_encoding)
            face_distances = face_recognition.face_distance(list(known_encodings.values()), face_encoding)
            best_match_index = np.argmin(face_distances) if len(face_distances) > 0 else None
            
            if best_match_index is not None and matches[best_match_index]:
                student_id = list(known_encodings.keys())[best_match_index]
                mark_attendance(student_id)
        
        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

# FastAPI setup
app = FastAPI()

@app.post("/register/")
def api_register_student(name: str = Form(...), image_file: UploadFile = File(...)):
    return register_student(name, image_file)

@app.get("/recognize/")
def api_recognize_faces():
    recognize_faces()
    return {"message": "Face recognition started"}

if __name__ == "__main__":
    create_tables()
    uvicorn.run(app, host="0.0.0.0", port=8000)
