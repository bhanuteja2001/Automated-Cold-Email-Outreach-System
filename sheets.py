import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
import random
import datetime

# Authorize the API
scope = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
]
file_name = "client_key.json"
creds = ServiceAccountCredentials.from_json_keyfile_name(file_name, scope)
client = gspread.authorize(creds)


class RecruiterDataFetch:
    @staticmethod
    def recruiter_all_records():
        # Fetch the sheet
        sheet = client.open("RecruiterEmailList").sheet1
        python_sheet = sheet.get_values("A:G")

        # Skip the header and filter records where the Status (E column) is not equal to "Email Sent"
        filtered_records = [row for row in python_sheet[1:] if row[4] != "Email Sent" and row[0]] 

        pp = pprint.PrettyPrinter()
        # pp.pprint(filtered_records)  # Uncomment for debugging

        # Select one random record from filtered records if available
        if filtered_records:
            random_record = random.choice(filtered_records)
            print("Selected a random record")
            return random_record
        return None

    @staticmethod
    def add_new_entry(entry):
        sheet = client.open("RecruiterEmailList").sheet1
        sheet.append_row(entry)

    @staticmethod
    def update_status(people):
        sheet = client.open("RecruiterEmailList").sheet1

        for person in people:
            if (
                person and "ID" in person
            ):  # Check if 'ID' exists in the person dictionary
                id_to_update = person["ID"]  # Assuming ID is stored in 'ID'
                status = "Email Sent"  # New status to set
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cell = sheet.find(str(id_to_update))  # Find the cell with the ID
                if cell:
                    sheet.update_cell(cell.row, 5, status)  # E column is the 5th column
                    sheet.update_cell(cell.row, 7, timestamp)  # G column for timestamp
