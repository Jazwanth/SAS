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

def load_face_encodings():
    conn = connect_db()
    if not conn:
        return {}

    cursor = conn.cursor()
    cursor.execute("SELECT id, face_encoding FROM students")
    encodings = {}
    
    for student_id, encoding_str in cursor.fetchall():
        try:
            encoding = np.array(eval(encoding_str))  # Convert string back to numpy array
            encodings[student_id] = encoding
        except Exception as e:
            print(f"⚠️ Error decoding student ID {student_id}: {e}")

    cursor.close()
    conn.close()
    return encodings

def mark_attendance(student_id):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO attendance (student_id) VALUES (%s)", (student_id,))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Attendance marked for student ID {student_id}")

def recognize_faces():
    known_encodings = load_face_encodings()
    
    if not known_encodings:
        print("⚠️ No student face encodings found in the database.")
        return

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame, model='hog')
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, model='small')

        print(f"👀 Detected {len(face_locations)} faces")  # Debugging output

        for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(list(known_encodings.values()), face_encoding)
            face_distances = face_recognition.face_distance(list(known_encodings.values()), face_encoding)
            best_match_index = np.argmin(face_distances) if len(face_distances) > 0 else None

            if best_match_index is not None and matches[best_match_index]:
                student_id = list(known_encodings.keys())[best_match_index]
                mark_attendance(student_id)
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, f"ID: {student_id}", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            else:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(frame, "Unknown", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        cv2.imshow("Face Recognition", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    recognize_faces()
