import cv2
import numpy as np
import mysql.connector
from datetime import datetime
import os
import pickle

class AttendanceSystem:
    def __init__(self):
        # MySQL Configuration
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="attendance_system"
        )
        self.cursor = self.db.cursor()
        
        # Initialize face detector
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Initialize LBPH Face Recognizer
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Create necessary directories
        if not os.path.exists('dataset'):
            os.makedirs('dataset')
        
        # Setup database and load recognizer
        self.setup_database()
        self.load_recognizer()
        
        # Dictionary to store id->name mapping
        self.id_name_map = {}
        self.load_id_name_map()

    def setup_database(self):
        # Create users table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                registration_date DATETIME
            )
        """)
        
        # Create attendance table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                check_in DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        self.db.commit()

    def load_id_name_map(self):
        self.cursor.execute("SELECT id, name FROM users")
        for (id, name) in self.cursor:
            self.id_name_map[id] = name

    def load_recognizer(self):
        if os.path.exists('recognizer.yml'):
            self.recognizer.read('recognizer.yml')

    def register_new_user(self):
        name = input("Enter the name of the person: ")
        
        # Insert user into database
        sql = "INSERT INTO users (name, registration_date) VALUES (%s, %s)"
        values = (name, datetime.now())
        self.cursor.execute(sql, values)
        self.db.commit()
        user_id = self.cursor.lastrowid
        
        # Update id->name mapping
        self.id_name_map[user_id] = name
        
        # Capture face images for training
        cap = cv2.VideoCapture(0)
        face_samples = []
        sample_count = 0
        
        print("Looking straight at the camera, press 'c' to capture samples (need 20 samples)")
        
        while True:
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            cv2.imshow('Registration', frame)
            
            key = cv2.waitKey(1)
            if key == ord('c'):
                if len(faces) == 1:
                    x, y, w, h = faces[0]
                    face_sample = gray[y:y+h, x:x+w]
                    face_sample = cv2.resize(face_sample, (200, 200))
                    face_samples.append(face_sample)
                    sample_count += 1
                    print(f"Captured sample {sample_count}/20")
                    
                    if sample_count >= 20:
                        break
                else:
                    print("Please ensure exactly one face is visible")
            
            elif key == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        if sample_count >= 20:
            # Train recognizer with new samples
            labels = [user_id] * len(face_samples)
            self.recognizer.update(face_samples, np.array(labels))
            self.recognizer.write('recognizer.yml')
            print(f"Successfully registered {name}")
        else:
            print("Registration incomplete - not enough samples")

    def mark_attendance(self):
        cap = cv2.VideoCapture(0)
        print("Press 'a' to mark attendance when your face is visible")
        
        while True:
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                face = gray[y:y+h, x:x+w]
                face = cv2.resize(face, (200, 200))
                
                # Predict the face
                user_id, confidence = self.recognizer.predict(face)
                
                # Get name from id->name mapping
                name = self.id_name_map.get(user_id, "Unknown")
                
                # Draw rectangle and name
                color = (0, 255, 0) if confidence < 100 else (0, 0, 255)
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(frame, f"{name} ({confidence:.1f})", 
                           (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            
            cv2.imshow('Attendance System', frame)
            
            key = cv2.waitKey(1)
            if key == ord('a'):
                if len(faces) == 1:
                    face = gray[y:y+h, x:x+w]
                    face = cv2.resize(face, (200, 200))
                    user_id, confidence = self.recognizer.predict(face)
                    
                    if confidence < 100:  # Threshold for recognition
                        # Record attendance
                        sql = "INSERT INTO attendance (user_id, check_in) VALUES (%s, %s)"
                        values = (user_id, datetime.now())
                        self.cursor.execute(sql, values)
                        self.db.commit()
                        
                        print(f"Attendance marked for {self.id_name_map[user_id]}")
                        break
                    else:
                        print("Face not recognized with sufficient confidence")
                else:
                    print("Please ensure exactly one face is visible")
            
            elif key == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

    def view_attendance(self):
        self.cursor.execute("""
            SELECT users.name, attendance.check_in 
            FROM attendance 
            JOIN users ON attendance.user_id = users.id 
            ORDER BY attendance.check_in DESC
        """)
        
        print("\nAttendance Records:")
        print("Name | Check-in Time")
        print("-" * 30)
        for (name, check_in) in self.cursor:
            print(f"{name} | {check_in}")

def main():
    system = AttendanceSystem()
    
    while True:
        print("\n1. Register New User")
        print("2. Mark Attendance")
        print("3. View Attendance")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '1':
            system.register_new_user()
        elif choice == '2':
            system.mark_attendance()
        elif choice == '3':
            system.view_attendance()
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()