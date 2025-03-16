import cv2
import numpy as np
import face_recognition
import mysql.connector
from database_setup import connect_db

def load_face_encodings():
    """Loads face encodings and names from the database."""
    conn = connect_db()
    if not conn:
        return {}, {}
    
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, face_encoding FROM students")
    known_encodings = {}
    student_names = {}
    
    for student_id, name, encoding_str in cursor.fetchall():
        encoding = np.array(eval(encoding_str))
        known_encodings[student_id] = encoding
        student_names[student_id] = name
    
    cursor.close()
    conn.close()
    return known_encodings, student_names

def mark_attendance(student_id):
    """Marks attendance in the database."""
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO attendance (student_id) VALUES (%s)", (student_id,))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Attendance marked for {student_id}")

def recognize_faces():
    """Detect and recognize faces in real-time."""
    known_encodings, student_names = load_face_encodings()
    if not known_encodings:
        print("⚠️ No student face encodings found in the database.")
        return
    
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(list(known_encodings.values()), face_encoding)
            face_distances = face_recognition.face_distance(list(known_encodings.values()), face_encoding)
            best_match_index = np.argmin(face_distances) if len(face_distances) > 0 else None
            
            if best_match_index is not None and matches[best_match_index]:
                student_id = list(known_encodings.keys())[best_match_index]
                name = student_names[student_id]
                mark_attendance(student_id)
                
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    recognize_faces()
