# Face Recognition Attendance System

This project is a Python-based **Face Recognition Attendance System** designed to streamline the process of recording attendance using facial recognition technology. It leverages OpenCV for face detection and recognition, and MySQL for managing user and attendance data.

---

## Features

### 1. User Registration
- Allows the registration of new users with their name.
- Captures 20 facial samples using a webcam.
- Trains the system to recognize the new user.
- Stores user data in a MySQL database.

### 2. Mark Attendance
- Recognizes faces in real-time using a webcam.
- Links recognized faces to registered users.
- Records attendance with a timestamp in the database.

### 3. View Attendance Records
- Displays a log of attendance records.
- Fetches data directly from the database.

---

## Prerequisites

### Software Requirements
- Python 3.7 or higher
- MySQL Server

### Python Libraries
Install the following Python libraries:
```bash
pip install mysql-connector-python opencv-python numpy
```

---

## Installation and Setup

### 1. Clone the Repository
```bash
git clone <repo-url>
cd <repo-directory>
```

### 2. Configure the Database
- Create a MySQL database named `attendance_system`.
- Ensure MySQL server is running.
- Update the MySQL connection details in the code (`host`, `user`, `password`, and `database`) if necessary.

### 3. Run the Application
Run the script using Python:
```bash
python attendance_system.py
```

---

## Usage

The system provides an interactive menu with the following options:

1. **Register New User**
   - Add a new user by entering their name.
   - Capture facial samples and train the system.

2. **Mark Attendance**
   - Recognize faces and mark attendance for registered users.

3. **View Attendance**
   - View all attendance records, including names and timestamps.

4. **Exit**
   - Close the application.

---

## Project Structure

- **Database**
  - `users` table: Stores user information (ID, name, registration date).
  - `attendance` table: Records attendance data (user ID, check-in time).

- **Directories**
  - `dataset`: Stores facial samples (created automatically if not present).
  - `recognizer.yml`: Stores the trained facial recognition model.

---

## Notes

- Ensure a functional webcam is connected to your system.
- Facial recognition confidence threshold can be adjusted in the code for better accuracy.
- Attendance marking requires exactly one face to be visible in the frame.

---

## Contribution

Contributions are welcome! Feel free to:
- Submit issues for bugs or feature requests.
- Create pull requests to improve the system.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Acknowledgements

- OpenCV for providing robust face detection and recognition capabilities.
- MySQL for efficient database management.

