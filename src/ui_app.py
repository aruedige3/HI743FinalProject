import tkinter as tk
from tkinter import messagebox, simpledialog
import os
from datetime import datetime
from classes import PatientDatabase, Patient, User
from authentication import authenticate_user
from utils import generate_random_id
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class PatientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Patient Management System")
        self.username = None
        self.user = None
        self.patient_db = None

        self.login_screen()

    def login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Username").grid(row=0, column=0)
        tk.Label(self.root, text="Password").grid(row=1, column=0)

        self.username_entry = tk.Entry(self.root)
        self.password_entry = tk.Entry(self.root, show="*")

        self.username_entry.grid(row=0, column=1)
        self.password_entry.grid(row=1, column=1)

        tk.Button(self.root, text="Login", command=self.authenticate).grid(row=2, columnspan=2)

    def authenticate(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        users = User.from_csv(os.path.join(BASE_DIR, 'Credentials.csv'))
        self.user = users.get(username)

        if self.user and self.user.authenticate(password):
            self.username = username
            self.patient_db = PatientDatabase(os.path.join(BASE_DIR, 'Patient_data.csv'))
            self.show_menu()
            self.log_activity("login")
        else:
            self.log_activity("failed_login", username=username)
            messagebox.showerror("Error", "Invalid credentials")

    def show_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        role = self.user.role
        if role == "management":
            tk.Button(self.root, text="Generate key statistics", command=self.generate_statistics).pack(pady=5)
            tk.Button(self.root, text="Exit", command=self.root.quit).pack(pady=5)
        elif role in ["nurse", "clinician"]:
            tk.Button(self.root, text="Retrieve Patient", command=self.retrieve_patient).pack(pady=5)
            tk.Button(self.root, text="Add Patient", command=self.add_patient).pack(pady=5)
            tk.Button(self.root, text="Remove Patient", command=self.remove_patient).pack(pady=5)
            tk.Button(self.root, text="Count Visits", command=self.count_visits).pack(pady=5)
            tk.Button(self.root, text="View Note", command=self.view_note).pack(pady=5)
            tk.Button(self.root, text="Exit", command=self.root.quit).pack(pady=5)
        elif role == "admin":
            tk.Button(self.root, text="Count Visits", command=self.count_visits).pack(pady=5)
            tk.Button(self.root, text="Exit", command=self.root.quit).pack(pady=5)

    def retrieve_patient(self):
        patient_id = simpledialog.askstring("Input", "Enter Patient ID:")
        if not patient_id:
            return
        patient = self.patient_db.patients.get(patient_id)
        if patient:
            visits = '\n'.join([f"{v['Visit_ID']} at {v['Visit_time']}" for v in patient.visits])
            info = (f"Patient ID: {patient.patient_id}\nGender: {patient.gender}\nRace: {patient.race}\n"
                    f"Ethnicity: {patient.ethnicity}\nAge: {patient.age}\nZip Code: {patient.zip_code}\n"
                    f"Insurance: {patient.insurance}\nVisits:\n{visits}")
            messagebox.showinfo("Patient Info", info)
        else:
            messagebox.showerror("Error", "Patient not found.")
        self.log_activity("retrieve_patient")

    def add_patient(self):
        patient_id = simpledialog.askstring("Input", "Enter Patient ID:")
        if not patient_id:
            return

        if patient_id in self.patient_db.patients:
            visit_time = simpledialog.askstring("Input", "Enter Visit Time:")
            visit_id = generate_random_id()
            self.patient_db.patients[patient_id].add_visit(visit_id, visit_time)
            messagebox.showinfo("Success", f"Visit added for patient {patient_id}")
        else:
            gender = simpledialog.askstring("Input", "Enter Gender:")
            race = simpledialog.askstring("Input", "Enter Race:")
            ethnicity = simpledialog.askstring("Input", "Enter Ethnicity:")
            age = simpledialog.askstring("Input", "Enter Age:")
            zip_code = simpledialog.askstring("Input", "Enter Zip Code:")
            insurance = simpledialog.askstring("Input", "Enter Insurance:")
            visit_time = simpledialog.askstring("Input", "Enter Visit Time:")
            visit_id = generate_random_id()
            new_patient = Patient(patient_id, gender, race, ethnicity, age, zip_code, insurance)
            new_patient.add_visit(visit_id, visit_time)
            self.patient_db.patients[patient_id] = new_patient
            messagebox.showinfo("Success", f"New patient {patient_id} added.")

        self.patient_db.save_patient_data()
        self.log_activity("add_patient")

    def remove_patient(self):
        patient_id = simpledialog.askstring("Input", "Enter Patient ID to remove:")
        if not patient_id:
            return
        if patient_id in self.patient_db.patients:
            del self.patient_db.patients[patient_id]
            self.patient_db.save_patient_data()
            messagebox.showinfo("Success", f"Patient {patient_id} removed.")
        else:
            messagebox.showerror("Error", "Patient not found.")
        self.log_activity("remove_patient")

    def count_visits(self):
        date_input = simpledialog.askstring("Input", "Enter date (MM/DD/YYYY):")
        if not date_input:
            return
        try:
            target_date = datetime.strptime(date_input, "%m/%d/%Y").strftime("%m/%d/%Y")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format.")
            return

        df = pd.read_csv(os.path.join(BASE_DIR, 'Patient_data.csv'))
        visit_time_columns = [col for col in df.columns if col.startswith("Visit_time")]

        visit_count = 0
        for col in visit_time_columns:
            for val in df[col].dropna():
                val = str(val).strip()
                try:
                    visit_date = datetime.strptime(val.split()[0], "%m/%d/%Y").strftime("%m/%d/%Y")
                    if visit_date == target_date:
                        visit_count += 1
                except:
                    continue

        messagebox.showinfo("Visit Count", f"Total visits on {target_date}: {visit_count}")
        self.log_activity("count_visits")

    def view_note(self):
        note_id = simpledialog.askstring("Input", "Enter Note ID:")
        if not note_id:
            return
        note = self.patient_db.get_note_by_id(note_id)
        if note:
            messagebox.showinfo(f"Note {note_id}", note)
        else:
            messagebox.showerror("Error", "Note not found.")
        self.log_activity("view_note")

    def generate_statistics(self):
        df = pd.read_csv(os.path.join(BASE_DIR, 'Patient_data.csv'))
        visit_time_columns = [col for col in df.columns if col.startswith("Visit_time")]

        visits_per_day = {}
        for col in visit_time_columns:
            for val in df[col].dropna():
                val = str(val).strip()
                try:
                    visit_date = datetime.strptime(val.split()[0], "%m/%d/%Y").strftime("%m/%d/%Y")
                    visits_per_day[visit_date] = visits_per_day.get(visit_date, 0) + 1
                except:
                    continue

        if not visits_per_day:
            messagebox.showinfo("Stats", "No visit times found.")
            return

        stats_str = "\n".join([f"{date}: {count} visit(s)" for date, count in sorted(visits_per_day.items())])
        messagebox.showinfo("Key Statistics", stats_str)
        self.log_activity("generate_statistics")

    def log_activity(self, action, username=None, role=None):
        log_file = os.path.join(BASE_DIR, "user_activity_log.txt")
        log_username = username if username is not None else getattr(self, 'username', 'Unknown')
        log_role = role if role is not None else getattr(getattr(self, 'user', None), 'role', 'Unknown')
    
        with open(log_file, "a") as f:
            f.write(f"{datetime.now()}, {log_username}, {log_role}, {action}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = PatientApp(root)
    root.mainloop()
