import cv2
import numpy as np
import face_recognition
import mysql.connector

# Database connection details
DB_HOST = "localhost"
DB_USER = "Smart_Attendance_Admin"
DB_PASSWORD = "Smart_MEC"
DB_NAME = "attendance_db"

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

def register_student(name):
    cap = cv2.VideoCapture(0)
    print("📸 Capturing face. Please look at the camera...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to capture image")
            break
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        if face_encodings:
            encoding_str = str(face_encodings[0].tolist())  # Convert encoding to string
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO students (name, face_encoding) VALUES (%s, %s)", (name, encoding_str))
                conn.commit()
                cursor.close()
                conn.close()
                print(f"✅ Student '{name}' registered successfully!")
            break
        
        cv2.imshow("Registering Face", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    student_name = input("Enter student's name: ")
    register_student(student_name)
