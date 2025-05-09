import argparse
from datetime import datetime, timedelta
import pandas as pd
from classes import PatientDatabase, User
from authentication import authenticate_user
from utils import generate_random_id

def main():
    parser = argparse.ArgumentParser(description="Patient Management System")
    parser.add_argument('-username', required=True, help="Username for authentication")
    parser.add_argument('-password', required=True, help="Password for authentication")
    args = parser.parse_args()

    users = User.from_csv('./Credentials.csv')

    user = users.get(args.username)
    if user is None or not user.authenticate(args.password):
        print("Invalid credentials. Access denied.")
        return

    patient_db = PatientDatabase('./Patient_data.csv')


    if user.role == 'management':
        print("Generating temporal trend of patient visits...")

        df = pd.read_csv('./Patient_data.csv')
        visits_per_day = {}

        visit_time_columns = [col for col in df.columns if col.startswith("Visit_time_")]

        for col in visit_time_columns:
            for val in df[col].dropna():
                val = str(val).strip()
                if val:
                    visit_date = val.split()[0]
                    visits_per_day[visit_date] = visits_per_day.get(visit_date, 0) + 1

        print("\nDaily Patient Visit Counts:")
        if not visits_per_day:
            print("No visit times found.")
        else:
            for date in sorted(visits_per_day.keys()):
                print(f"{date}: {visits_per_day[date]} visit(s)")

    if user.role == 'management':
        df = pd.read_csv('./Patient_data.csv')
        visit_time_columns = [col for col in df.columns if col.startswith("Visit_time_")]

        current_date = datetime.now()
        start_date = (current_date - timedelta(days=365)).strftime("%m/%d/%Y")
        end_date = current_date.strftime("%m/%d/%Y")

        print(f"Counting visits from {start_date} to {end_date}...")

        visits_per_day = {}

        for col in visit_time_columns:
            for val in df[col].dropna():
                val = str(val).strip()
                if val:
                    try:
                        visit_datetime = datetime.strptime(val.split()[0], "%m/%d/%Y")
                        visit_date = visit_datetime.strftime("%m/%d/%Y")

                        if start_date <= visit_date <= end_date:
                            visits_per_day[visit_date] = visits_per_day.get(visit_date, 0) + 1
                    except ValueError:
                        print(f"Skipping unrecognized date format: {val}")
                        continue

        print("\nTotal Visits in the Last Year:")
        if not visits_per_day:
            print("No visits found in the specified range.")
        else:
            for date in sorted(visits_per_day.keys()):
                print(f"{date}: {visits_per_day[date]} visit(s)")

    if user.role == 'admin':
        df = pd.read_csv('./Patient_data.csv')
        visit_time_columns = [col for col in df.columns if col.startswith("Visit_time")]

        date_input = input("Enter date (MM/DD/YYYY): ").strip()
        try:
            target_date = datetime.strptime(date_input, "%m/%d/%Y").strftime("%m/%d/%Y")
        except ValueError:
            print("Invalid date format. Please use MM/DD/YYYY.")
            return

        visit_count = 0
        for col in visit_time_columns:
            for val in df[col].dropna():
                val = str(val).strip() 

                if val:
                    try:
                        visit_date = datetime.strptime(val.split()[0], "%m/%d/%Y").strftime("%m/%d/%Y")
                    
                        if visit_date == target_date:
                            visit_count += 1
                    except ValueError:
                        print(f"Skipping unrecognized date format: {val}")
                        continue

        print(f"\nTotal visits on {target_date}: {visit_count} visit(s)")
        return


    if user.role in ['nurse', 'clinician']:
        while True:
            action = input("Enter action (add_patient, remove_patient, retrieve_patient, count_visits, view_note, stop): ")
            if action == 'add_patient':
                patient_id = input("Enter Patient_ID: ").strip()
                if patient_id in patient_db.patients:
                    visit_time = input("Enter Visit_time: ")
                    visit_id = generate_random_id()
                    patient_db.patients[patient_id].add_visit(visit_id, visit_time)
                    patient_db.save_patient_data()
                    print(f"Visit added for patient {patient_id}.")
                else:
                    gender = input("Enter gender: ")
                    race = input("Enter race: ")
                    ethnicity = input("Enter ethnicity: ")
                    age = input("Enter age: ")
                    zip_code = input("Enter zip code: ")
                    insurance = input("Enter insurance: ")
                    new_patient = Patient(patient_id, gender, race, ethnicity, age, zip_code, insurance)
                    visit_time = input("Enter Visit_time: ")
                    visit_id = generate_random_id()
                    new_patient.add_visit(visit_id, visit_time)
                    patient_db.patients[patient_id] = new_patient
                    patient_db.save_patient_data()
                    print(f"New patient {patient_id} added.")
            elif action == 'remove_patient':
                patient_id = input("Enter Patient_ID: ").strip()
                if patient_id in patient_db.patients:
                    del patient_db.patients[patient_id]
                    patient_db.save_patient_data()
                    print(f"Patient {patient_id} removed.")
                else:
                    print("Patient not found.")
            elif action == 'retrieve_patient':
                patient_id = input("Enter Patient_ID: ").strip()
                if patient_id in patient_db.patients:
                    patient = patient_db.patients[patient_id]
                    print(f"Patient ID: {patient.patient_id}, Gender: {patient.gender}, Race: {patient.race}, "
                          f"Ethnicity: {patient.ethnicity}, Age: {patient.age}, Zip Code: {patient.zip_code}, "
                          f"Insurance: {patient.insurance}")
                    for visit in patient.visits:
                        print(f"Visit ID: {visit['Visit_ID']}, Visit Time: {visit['Visit_time']}")
                else:
                    print("Patient not found.")
            elif action == 'count_visits':
                df = pd.read_csv('./Patient_data.csv')
                visit_time_columns = [col for col in df.columns if col.startswith("Visit_time")]

                date_input = input("Enter date (MM/DD/YYYY): ").strip()
                try:
                    target_date = datetime.strptime(date_input, "%m/%d/%Y").strftime("%m/%d/%Y")
                except ValueError:
                    print("Invalid date format. Please use MM/DD/YYYY.")
                    return

                visit_count = 0
                for col in visit_time_columns:
                    for val in df[col].dropna():
                        val = str(val).strip() 

                        if val:
                            try:
                                visit_date = datetime.strptime(val.split()[0], "%m/%d/%Y").strftime("%m/%d/%Y")
                    
                                if visit_date == target_date:
                                    visit_count += 1
                            except ValueError:
                                print(f"Skipping unrecognized date format: {val}")
                                continue

                print(f"\nTotal visits on {target_date}: {visit_count} visit(s)")
                return
            elif action == 'view_note':
                note_id = input("Enter Note_ID to view: ").strip()

                if not note_id:
                    print("No Note_ID entered. Please try again.")
                else:
                    note = patient_db.get_note_by_id(note_id) 
                if note:
                    print(f"\n📄 Clinical Note (ID: {note_id}):\n{'-'*40}")
                    print(note)
                    print('-'*40 + '\n')
                else:
                    print(f"No clinical note found with Note_ID: {note_id}\n")
            elif action == 'stop':
                break
            else:
                print("Invalid action. Please try again.")

if __name__ == "__main__":
    main()
