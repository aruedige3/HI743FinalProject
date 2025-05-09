import pandas as pd
from datetime import datetime


class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role

    @classmethod
    def from_csv(cls, file_path):
        df = pd.read_csv(file_path)
        users = {}
        for _, row in df.iterrows():
            users[row['username']] = cls(row['username'], row['password'], row['role'])
        return users

    def authenticate(self, input_password):
        return self.password == input_password


class Patient:
    def __init__(self, patient_id, gender, race, ethnicity, age, zip_code, insurance):
        self.patient_id = patient_id
        self.gender = gender
        self.race = race
        self.ethnicity = ethnicity
        self.age = age
        self.zip_code = zip_code
        self.insurance = insurance
        self.visits = []

    def add_visit(self, visit_id, visit_time):
        self.visits.append({'Visit_ID': visit_id, 'Visit_time': visit_time})


class PatientDatabase:
    def __init__(self, file_path):
        self.file_path = file_path
        self.patients = self.load_patients_from_csv()
        self.notes = self.load_notes_from_csv('./Notes.csv')

    def load_patients_from_csv(self):
        df = pd.read_csv(self.file_path)
        patients = {}
        for _, row in df.iterrows():
            patient = Patient(
                patient_id=row['Patient_ID'],
                gender=row['Gender'],
                race=row['Race'],
                ethnicity=row['Ethnicity'],
                age=row['Age'],
                zip_code=row['Zip_code'],
                insurance=row['Insurance']
            )
            visits = []
            for col in df.columns:
                if col.startswith("Visit_ID"):
                    index = col.split("_")[-1]
                    visit_data = {
                        'Visit_ID': row[col],
                        'Visit_time': row.get(f"Visit_time_{index}", "")
                    }
                    visits.append(visit_data)
            patient.visits = visits
            patients[patient.patient_id] = patient
        return patients

    def load_notes_from_csv(self, notes_path):
        df = pd.read_csv(notes_path)
        notes = {}
        for _, row in df.iterrows():
            notes[str(row['Note_ID'])] = row['Note_text']
        return notes

    def save_patient_data(self):
        patient_data = []
        for patient in self.patients.values():
            row = {
                'Patient_ID': patient.patient_id,
                'Gender': patient.gender,
                'Race': patient.race,
                'Ethnicity': patient.ethnicity,
                'Age': patient.age,
                'Zip_code': patient.zip_code,
                'Insurance': patient.insurance
            }
            for idx, visit in enumerate(patient.visits, 1):
                row[f"Visit_ID_{idx}"] = visit.get('Visit_ID')
                row[f"Visit_time_{idx}"] = visit.get('Visit_time')
            patient_data.append(row)
        df = pd.DataFrame(patient_data)
        df.to_csv(self.file_path, index=False)

    def count_visits_on_date(self, date):
        count = 0
        for patient in self.patients.values():
            for visit in patient.visits:
                if visit.get('Visit_time', '').startswith(date):
                    count += 1
        return count

    def get_note_by_id(self, note_id):
        return self.notes.get(note_id, None)
