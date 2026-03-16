import cv2
import face_recognition
import numpy as np
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class FaceRecognitionSystem:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True
        self.known_faces_dir = "known_faces"
        self.frame_count = 0
        self.last_processed_frame = None
        self.last_processed_names = []
        self.initialize_known_faces()

    def initialize_known_faces(self):
        """Initialize known faces from the known_faces directory."""
        try:
            if not os.path.exists(self.known_faces_dir):
                os.makedirs(self.known_faces_dir)
                logging.info(f"Created directory: {self.known_faces_dir}")
                return

            face_files = [f for f in os.listdir(self.known_faces_dir) 
                         if f.lower().endswith((".jpg", ".jpeg", ".png"))]
            
            if not face_files:
                logging.warning("No face images found in known_faces directory")
                return

            for filename in face_files:
                try:
                    image_path = os.path.join(self.known_faces_dir, filename)
                    face_image = face_recognition.load_image_file(image_path)
                    face_encoding = face_recognition.face_encodings(face_image)

                    if face_encoding:
                        self.known_face_encodings.append(face_encoding[0])
                        name = os.path.splitext(filename)[0]
                        self.known_face_names.append(name)
                        logging.info(f"Loaded face: {name}")
                    else:
                        logging.warning(f"No face detected in {filename}")
                except Exception as e:
                    logging.error(f"Error processing {filename}: {str(e)}")

            logging.info(f"Loaded {len(self.known_face_names)} known faces")
        except Exception as e:
            logging.error(f"Error initializing known faces: {str(e)}")

    def add_new_face(self, image, name):
        """Add a new face to the known faces database."""
        try:
            if image is None or image.size == 0:
                logging.error("Invalid image provided")
                return False

            # Convert image to RGB if it's in BGR format
            if len(image.shape) == 3 and image.shape[2] == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = image

            face_encoding = face_recognition.face_encodings(rgb_image)
            
            if face_encoding:
                self.known_face_encodings.append(face_encoding[0])
                self.known_face_names.append(name)
                
                if not os.path.exists(self.known_faces_dir):
                    os.makedirs(self.known_faces_dir)
                
                filename = f"{name}.jpg"
                filepath = os.path.join(self.known_faces_dir, filename)
                cv2.imwrite(filepath, image)
                logging.info(f"Added new face: {name}")
                return True
            else:
                logging.warning(f"No face detected in the image for {name}")
                return False
        except Exception as e:
            logging.error(f"Error adding new face: {str(e)}")
            return False

    def process_frame(self, frame):
        """Process a single frame for face recognition."""
        try:
            if frame is None or frame.size == 0:
                logging.error("Invalid frame received")
                return frame, []

            # Process every 4th frame instead of 8th to catch more faces
            self.frame_count += 1
            if self.frame_count % 4 != 0:
                # Return the last processed frame and names if available
                if self.last_processed_frame is not None:
                    return self.last_processed_frame, self.last_processed_names
                return frame, []

            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            
            # Convert BGR to RGB
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Find face locations and encodings
            self.face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
            self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

            self.face_names = []
            for face_encoding in self.face_encodings:
                # Increase tolerance to 0.7 to be more lenient with face matching
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.7)
                name = "Unknown"

                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.known_face_names[first_match_index]
                    logging.info(f"Recognized face: {name}")  # Add logging for successful recognition

                self.face_names.append(name)

            # Create a copy of the frame for drawing
            display_frame = frame.copy()

            # Display results
            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                # Scale back up face locations
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw box around face
                cv2.rectangle(display_frame, (left, top), (right, bottom), (0, 255, 0), 2)

                # Draw label
                cv2.rectangle(display_frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(display_frame, name, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)

            # Store the processed frame and names for future use
            self.last_processed_frame = display_frame
            self.last_processed_names = self.face_names.copy()

            return display_frame, self.face_names
        except Exception as e:
            logging.error(f"Error processing frame: {str(e)}")
            return frame, [] 