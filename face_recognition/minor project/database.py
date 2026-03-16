import pandas as pd
from datetime import datetime
import os
import logging
from typing import Optional, List, Dict

class AttendanceDatabase:
    def __init__(self):
        self.attendance_file = "attendance.csv"
        self.backup_file = "attendance_backup.csv"
        self.initialize_database()

    def initialize_database(self):
        """Initialize the attendance database if it doesn't exist."""
        try:
            if not os.path.exists(self.attendance_file):
                df = pd.DataFrame(columns=['Name', 'Date', 'Time'])
                df.to_csv(self.attendance_file, index=False)
                logging.info("Created new attendance database")
            else:
                # Create backup of existing database
                if os.path.exists(self.attendance_file):
                    df = pd.read_csv(self.attendance_file)
                    df.to_csv(self.backup_file, index=False)
                    logging.info("Created backup of attendance database")
        except Exception as e:
            logging.error(f"Error initializing database: {str(e)}")
            raise

    def mark_attendance(self, name: str) -> bool:
        """Mark attendance for a recognized person."""
        try:
            if not name or name == "Unknown":
                logging.warning("Invalid name provided for attendance")
                return False

            current_time = datetime.now()
            date = current_time.strftime('%Y-%m-%d')
            time = current_time.strftime('%H:%M:%S')

            # Read existing attendance records
            df = pd.read_csv(self.attendance_file)
            
            # Check if attendance already marked for today
            today_attendance = df[(df['Name'] == name) & (df['Date'] == date)]
            
            if today_attendance.empty:
                new_record = pd.DataFrame({
                    'Name': [name],
                    'Date': [date],
                    'Time': [time]
                })
                df = pd.concat([df, new_record], ignore_index=True)
                df.to_csv(self.attendance_file, index=False)
                logging.info(f"Marked attendance for {name} on {date} at {time}")
                return True
            else:
                logging.info(f"Attendance already marked for {name} on {date}")
                return False
        except Exception as e:
            logging.error(f"Error marking attendance: {str(e)}")
            return False

    def get_attendance_report(self, date: Optional[str] = None) -> pd.DataFrame:
        """Get attendance report for a specific date or all dates."""
        try:
            df = pd.read_csv(self.attendance_file)
            if date:
                return df[df['Date'] == date]
            return df
        except Exception as e:
            logging.error(f"Error getting attendance report: {str(e)}")
            return pd.DataFrame()

    def export_attendance(self, filename: str = "attendance_report.csv") -> str:
        """Export attendance records to a CSV file."""
        try:
            df = pd.read_csv(self.attendance_file)
            
            # Sort by date and time
            df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
            df = df.sort_values('DateTime')
            df = df.drop('DateTime', axis=1)
            
            # Export to CSV
            df.to_csv(filename, index=False)
            logging.info(f"Exported attendance report to {filename}")
            return filename
        except Exception as e:
            logging.error(f"Error exporting attendance: {str(e)}")
            return ""

    def get_statistics(self) -> Dict:
        """Get attendance statistics."""
        try:
            df = pd.read_csv(self.attendance_file)
            if df.empty:
                return {
                    'total_records': 0,
                    'unique_names': 0,
                    'dates': []
                }

            return {
                'total_records': len(df),
                'unique_names': df['Name'].nunique(),
                'dates': sorted(df['Date'].unique().tolist())
            }
        except Exception as e:
            logging.error(f"Error getting statistics: {str(e)}")
            return {
                'total_records': 0,
                'unique_names': 0,
                'dates': []
            } 