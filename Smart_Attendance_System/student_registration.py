import cv2
import numpy as np
import face_recognition
import mysql.connector
import os

# Database connection details
DB_HOST = "localhost"
DB_USER = "Smart_Attendance_Admin"
DB_PASSWORD = "Smart_MEC"
DB_NAME = "attendance_db"

# Ensure the 'student_images' directory exists
IMAGE_DIR = "student_images"
os.makedirs(IMAGE_DIR, exist_ok=True)

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
        print("⚠️ Error connecting to database:", e)
        return None

# Capture a student's face using the camera
def capture_student_image(name):
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Camera could not be opened.")
        return None
    
    print("📸 Press 'SPACE' to capture the image, 'Q' to cancel.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to capture image.")
            break
        
        cv2.imshow("Capture Image", frame)

        key = cv2.waitKey(1)
        if key == ord(' '):  # Press SPACE to capture
            image_path = os.path.join(IMAGE_DIR, f"{name}.jpg")
            cv2.imwrite(image_path, frame)
            print(f"✅ Image saved: {image_path}")
            break
        elif key == ord('q'):  # Press Q to cancel
            print("❌ Image capture canceled.")
            cap.release()
            cv2.destroyAllWindows()
            return None
    
    cap.release()
    cv2.destroyAllWindows()
    return image_path

# Register the student
def register_student():
    name = input("Enter student's name: ").strip()
    
    if not name:
        print("❌ Name cannot be empty.")
        return
    
    image_path = capture_student_image(name)
    if not image_path:
        return
    
    image = cv2.imread(image_path)
    
    if image is None:
        print("❌ Error reading the captured image.")
        return
    
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_encodings = face_recognition.face_encodings(rgb_image)

    if not face_encodings:
        print("❌ No face detected. Try again with a clearer image.")
        return
    
    face_encoding_str = str(face_encodings[0].tolist())  # Convert numpy array to string for database storage
    
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name, face_encoding) VALUES (%s, %s)", (name, face_encoding_str))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ {name} has been registered successfully!")

# Run the script
if __name__ == "__main__":
    register_student()
