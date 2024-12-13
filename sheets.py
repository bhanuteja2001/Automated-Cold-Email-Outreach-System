import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
import random
import datetime
import pytz

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
    def get_all_records_by_company(company_name, designation):
        sheet = client.open("RecruiterEmailList").sheet1
        python_sheet = sheet.get_values("A:H")
        filtered_records = [row for row in python_sheet[1:] if row[0] and row[3] == str(company_name) and row[5] == str(designation)]
        return filtered_records
    
    @staticmethod
    def recruiter_all_records():
        sheet = client.open("RecruiterEmailList").sheet1
        python_sheet = sheet.get_values("A:H")
        filtered_records = [row for row in python_sheet[1:] if row[4] != "Email Sent" and row[0]] 

        pp = pprint.PrettyPrinter()
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
            if person and "ID" in person:
                id_to_update = person["ID"]
                status = "Email Sent"
                priority = "No Priority"
                cst = pytz.timezone('US/Central')
                cst_time = datetime.datetime.now(cst)
                timestamp = cst_time.strftime("%Y-%m-%d %H:%M:%S %Z")
                
                cell = sheet.find(str(id_to_update))
                if cell:
                    sheet.update_cell(cell.row, 5, status)  # E column for Status
                    sheet.update_cell(cell.row, 7, timestamp)  # G column for Timestamp
                    sheet.update_cell(cell.row, 8, priority)  # H column for Priority

    @staticmethod
    def fetch_priority_emails():
        sheet = client.open("RecruiterEmailList").sheet1
        all_data = sheet.get_values("A:H")
        priority_emails = [row for row in all_data[1:] if row[7] in ['High', 'Medium'] and row[4] != "Email Sent"]
        return priority_emails

    @staticmethod
    def update_email_status(email_data):
        sheet = client.open("RecruiterEmailList").sheet1
        cell = sheet.find(email_data["ID"])
        if cell:
            row = cell.row
            sheet.update_cell(row, 5, email_data["Status"])  # E column for Status
            sheet.update_cell(row, 7, email_data["Timestamp"])  # G column for Timestamp
            sheet.update_cell(row, 8, email_data["Priority"])  # H column for Priority

    @staticmethod
    def add_transaction(Transaction):
        sheet = client.open("RecruiterEmailList").worksheet("Sheet3")
        #new_row = [date, company, name, email, status, title, priority, bcc_emails]
        sheet.append_row(Transaction)

    @staticmethod
    def update_email_status_instant(email_data):
        sheet = client.open("RecruiterEmailList").sheet1
        cell = sheet.find(email_data[0])
        if cell:
            row = cell.row
            sheet.update_cell(row, 5, email_data[4])  # E column for Status
            sheet.update_cell(row, 7, email_data[6])  # G column for Timestamp
            sheet.update_cell(row, 8, email_data[7])  # H column for Priority