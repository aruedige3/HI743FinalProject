# HI743FinalProject
# Patient Management System

This is a Python-based GUI application for managing patient data with role-based access control. 

## Project Structure

├── authentication.py # Handles user login and password verification  
├── classes.py # Contains Patient, User, and PatientDatabase classes  
├── Credentials.csv # CSV file with user credentials (username, password, role)  
├── Notes.csv # Notes tied to specific note IDs  
├── Patient_data.csv # Main dataset containing patient info and visit data  
├── ui_app.py # The main GUI application  
├── utils.py # Utility functions (e.g., random ID generation)  
├── user_activity_log.txt # Log of user activity (auto-generated)  
└── README.md # Project documentation (this file)

## Requirements

- Python 3.x
- `pandas`
- `tkinter`
- `datetime`
- `os`
- `argparse`
- `random`
- `string`

To install the external dependency, run:

```bash
pip install pandas
```

## How to Run

1. Open Terminal and navigate to the project directory:

   ```bash
   cd ~/Insert/Path/Here
   ```

2. Run the following in Terminal:

```bash
python ui_app.py
```

3. Enter your username and password to log into the system. 

4. Complete tasks as needed by selecting the appropriate action button. Actions are listed based on your role permissions. Any new patient data entered is stored within the original patient data file, and all actions taken are logged within the user activity log.

5. Select the 'exit' button to end your session and close the program.
