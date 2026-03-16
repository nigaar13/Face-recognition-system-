# Face Recognition Attendance System

This is a Python-based Face Recognition Attendance System that uses computer vision to automatically mark attendance by recognizing faces.

## Features

- Real-time face detection and recognition
- Automatic attendance marking
- CSV export of attendance records
- Simple and intuitive interface

## Requirements

- Python 3.8 or higher
- Webcam
- Required Python packages (listed in requirements.txt)

## Installation

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the main application:
   ```
   python main.py
   ```
2. The system will start your webcam
3. It will automatically detect and recognize faces
4. Attendance will be marked in real-time
5. Attendance records can be exported to CSV

## Project Structure

- `main.py`: Main application file
- `face_recognition_system.py`: Core face recognition functionality
- `database.py`: Handles attendance data storage
- `requirements.txt`: List of required Python packages

## Note

Make sure you have good lighting conditions for better face recognition accuracy. 