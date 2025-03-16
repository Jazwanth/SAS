from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import mysql.connector
import cv2
import numpy as np
import face_recognition
import io
import uvicorn

# Initialize FastAPI app
app = FastAPI()

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="Smart_Attendance_Admin",
        password="Smart_MEC",
        database="attendance_db"
    )

# Ensure tables exist
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        face_encoding TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id))''')
    conn.commit()
    cursor.close()
    conn.close()

create_tables()

# Face registration endpoint
@app.post("/register/")
def register_user(name: str = Form(...), image: UploadFile = File(...)):
    try:
        image_bytes = image.file.read()
        np_img = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        face_encodings = face_recognition.face_encodings(img)
        
        if not face_encodings:
            raise HTTPException(status_code=400, detail="No face detected!")
        
        encoding_str = ",".join(map(str, face_encodings[0]))
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, face_encoding) VALUES (%s, %s)", (name, encoding_str))
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "User registered successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Face detection & attendance marking endpoint
@app.post("/mark-attendance/")
def mark_attendance(image: UploadFile = File(...)):
    try:
        image_bytes = image.file.read()
        np_img = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        face_encodings = face_recognition.face_encodings(img)
        
        if not face_encodings:
            raise HTTPException(status_code=400, detail="No face detected!")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, face_encoding FROM users")
        users = cursor.fetchall()
        
        for user in users:
            user_id, name, encoding_str = user
            stored_encoding = np.array(list(map(float, encoding_str.split(","))))
            
            if face_recognition.compare_faces([stored_encoding], face_encodings[0])[0]:
                cursor.execute("INSERT INTO attendance (user_id) VALUES (%s)", (user_id,))
                conn.commit()
                cursor.close()
                conn.close()
                return {"message": f"Attendance marked for {name}"}
        
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Face not recognized!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the API
if __name__ == "__main__":
    uvicorn.run("smart_attendance_backend:app", host="0.0.0.0", port=8000, reload=True)
