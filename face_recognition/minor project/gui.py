"""
Nigar : This is the main file which should to run to start the attendance system. 
12 may 2025 5:30 pm

"""

import tkinter as tk # this library is used to create the gui of the application
from tkinter import ttk, messagebox 
import cv2 # this library is used to capture the video from the camera
from PIL import Image, ImageTk # this library is used to display the image in the gui
import threading # this library is used to run the code in the background
import time # current time
import logging # this library is used to log the messages in the console
import sys
import random

from face_recognition_system import FaceRecognitionSystem
from database import AttendanceDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('face_recognition.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class FaceRecognitionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition Attendance System")
        self.root.geometry("1200x700")
        
        # Custom color theme
        self.bg_color = "#bfd6da"          # Dark background
        self.text_color = "#f5f5f5"        # Light gray text for contrast
        self.accent_color = "#394041"      # Purple accent
        self.button_color = "#394041"      # Purple for buttons
        self.section_bg = "#f5f5f5"        # Purple for sections
        self.border_color = "#394041"      # Purple border color
        
        self.root.configure(bg=self.bg_color)

        # Initialize systems
        self.face_system = FaceRecognitionSystem()
        self.attendance_db = AttendanceDatabase()
        self.video_capture = None
        self.is_running = False
        self.today_attendance = set()
        self.current_date = time.strftime('%Y-%m-%d')

        # Load today's attendance from database
        self.load_today_attendance()

        self.setup_gui()
        self.update_attendance_display()  # Add initial attendance display update
        self.start_camera()

    def setup_gui(self):
        # Create main frames with borders
        self.video_frame = ttk.Frame(self.root, padding="10", style="Bordered.TFrame")
        self.video_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.control_frame = ttk.Frame(self.root, padding="10", style="Bordered.TFrame")
        self.control_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=3)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Video display
        self.video_label = ttk.Label(self.video_frame, style="Bordered.TLabel")
        self.video_label.pack(expand=True, fill="both")

        # Control buttons
        style = ttk.Style()
        
        # Configure bordered styles
        style.configure("Bordered.TFrame",
            background=self.bg_color,
            borderwidth=2,
            relief="solid"
        )
        
        style.configure("Bordered.TLabel",
            background=self.bg_color,
            foreground=self.text_color,
            borderwidth=2,
            relief="solid"
        )
        
        style.configure("Custom.TButton", 
            padding=10, 
            font=('Georgia', 15),
            background=self.button_color,
            foreground="#0f0701",  # Dark text on purple button
            borderwidth=2,
            relief="raised"
        )
        
        # Configure other styles
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", 
            background=self.bg_color,
            foreground=self.text_color,
            font=('Helvetica', 10)
        )
        
        # Configure section styles with borders
        style.configure("Section.TLabelframe", 
            background=self.section_bg,
            foreground="#0f0701",  # Dark text on purple background
            borderwidth=2,
            relief="solid"
        )
        style.configure("Section.TLabelframe.Label", 
            background=self.section_bg,
            foreground="#0f0701",  # Dark text on purple background
            font=('Helvetica', 10, 'bold')
        )

        self.add_face_btn = ttk.Button(
            self.control_frame,
            text="Add New Face",
            command=self.add_new_face,
            style="Custom.TButton"
        )
        self.add_face_btn.pack(pady=10, fill="x")

        self.quit_btn = ttk.Button(
            self.control_frame,
            text="Quit",
            command=self.quit_application,
            style="Custom.TButton"
        )
        self.quit_btn.pack(pady=10, fill="x")

        # Status frame with border
        self.status_frame = ttk.LabelFrame(self.control_frame, text="Status", padding="10", style="Section.TLabelframe")
        self.status_frame.pack(pady=10, fill="x")

        self.status_label = ttk.Label(
            self.status_frame,
            text="System Ready",
            font=('Helvetica', 10),
            foreground="#0f0701",  # Dark text on purple background
            style="Bordered.TLabel"
        )
        self.status_label.pack(pady=5)

        # Today's attendance frame with border
        self.attendance_frame = ttk.LabelFrame(self.control_frame, text="Today's Attendance", padding="10", style="Section.TLabelframe")
        self.attendance_frame.pack(pady=10, fill="x", expand=True)

        self.attendance_text = tk.Text(
            self.attendance_frame,
            height=10,
            width=30,
            font=('Helvetica', 10),
            bg=self.section_bg,
            fg="#0f0701",  # Dark text on purple background
            relief="solid",
            borderwidth=2
        )
        self.attendance_text.pack(pady=5, fill="both", expand=True)
        self.attendance_text.config(state='disabled')

    def load_today_attendance(self):
        """Load today's attendance from the database."""
        try:
            # Get today's attendance from database
            today_records = self.attendance_db.get_attendance_report(self.current_date)
            if not today_records.empty:
                self.today_attendance = set(today_records['Name'].tolist())
                logging.info(f"Loaded {len(self.today_attendance)} attendance records for today")
        except Exception as e:
            logging.error(f"Error loading today's attendance: {str(e)}")

    def start_camera(self):
        """Initialize and start the camera."""
        try:
            self.video_capture = cv2.VideoCapture(0)
            if not self.video_capture.isOpened():
                raise Exception("Could not open video capture device")

            # Set camera properties
            self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.video_capture.set(cv2.CAP_PROP_FPS, 30)

            self.is_running = True
            self.update_video()
            logging.info("Camera started successfully")
        except Exception as e:
            logging.error(f"Error starting camera: {str(e)}")
            messagebox.showerror("Error", "Could not start camera")

    def update_video(self):
        """Update the video feed and process frames."""
        if not self.is_running:
            return

        try:
            ret, frame = self.video_capture.read()
            if ret:
                # Process frame
                processed_frame, face_names = self.face_system.process_frame(frame)

                # Check for new attendance
                new_date = time.strftime('%Y-%m-%d')
                if new_date != self.current_date:
                    self.today_attendance.clear()
                    self.current_date = new_date
                    self.load_today_attendance()
                    self.update_attendance_display()

                # Update attendance for all recognized faces
                for name in face_names:
                    if name != "Unknown":
                        # Add to today's attendance if not already present
                        if name not in self.today_attendance:
                            if self.attendance_db.mark_attendance(name):
                                self.today_attendance.add(name)
                                self.update_attendance_display()
                                self.show_attendance_notification(name)
                                # Update status to show who was just detected
                                self.status_label.config(text=f"Detected: {name}")

                # Convert frame to PhotoImage
                processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(processed_frame)
                imgtk = ImageTk.PhotoImage(image=img)
                
                # Update video display
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)

            # Schedule next update
            self.root.after(10, self.update_video)
        except Exception as e:
            logging.error(f"Error updating video: {str(e)}")

    def update_attendance_display(self):
        """Update the attendance display with current attendance records."""
        try:
            self.attendance_text.config(state='normal')
            self.attendance_text.delete(1.0, tk.END)
            
            if not self.today_attendance:
                self.attendance_text.insert(tk.END, "Waiting for face detection...")
            else:
                # Get today's records from database to show actual timestamps
                today_records = self.attendance_db.get_attendance_report(self.current_date)
                if not today_records.empty:
                    # Sort by time
                    today_records = today_records.sort_values('Time')
                    for _, record in today_records.iterrows():
                        self.attendance_text.insert(tk.END, f"✓ {record['Name']} - {record['Time']}\n")
                else:
                    self.attendance_text.insert(tk.END, "No attendance records for today")
            
            self.attendance_text.config(state='disabled')
            # Scroll to the bottom to show latest entries
            self.attendance_text.see(tk.END)
        except Exception as e:
            logging.error(f"Error updating attendance display: {str(e)}")

    def show_attendance_notification(self, name):
        """Show notification when attendance is marked."""
        try:
            # Update status label instead of showing popup
            self.status_label.config(text=f"Attendance marked for {name}")
            # Make the status label more visible
            self.status_label.configure(foreground="green")
            # Reset the color after 2 seconds
            self.root.after(2000, lambda: self.status_label.configure(foreground="black"))
        except Exception as e:
            logging.error(f"Error showing attendance notification: {str(e)}")

    def add_new_face(self):
        """Add a new face to the system."""
        if not self.is_running:
            return

        # Create a new window for name input
        name_window = tk.Toplevel(self.root)
        name_window.title("Add New Face")
        name_window.geometry("300x150")
        name_window.transient(self.root)
        name_window.grab_set()

        ttk.Label(
            name_window,
            text="Enter name for the new face:",
            padding="10"
        ).pack(pady=10)

        name_entry = ttk.Entry(name_window, width=30)
        name_entry.pack(pady=10)
        name_entry.focus_set()

        def on_submit():
            name = name_entry.get().strip()
            if name:
                ret, frame = self.video_capture.read()
                if ret and self.face_system.add_new_face(frame, name):
                    messagebox.showinfo("Success", f"Added new face: {name}")
                else:
                    messagebox.showerror("Error", "No face detected in the frame")
            name_window.destroy()

        ttk.Button(
            name_window,
            text="Submit",
            command=on_submit
        ).pack(pady=10)

        # Bind Enter key to submit
        name_window.bind('<Return>', lambda e: on_submit())

    def quit_application(self):
        """Clean up and quit the application."""
        try:
            self.is_running = False
            if self.video_capture is not None:
                self.video_capture.release()
            
            # Export final attendance report
            report_file = self.attendance_db.export_attendance()
            logging.info(f"Final attendance report exported to: {report_file}")
            
            self.root.quit()
        except Exception as e:
            logging.error(f"Error during application shutdown: {str(e)}")
            self.root.quit()

def main():
    """Main entry point of the application."""
    try:
        root = tk.Tk()
        app = FaceRecognitionGUI(root)
        root.mainloop()
    except Exception as e:
        logging.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
