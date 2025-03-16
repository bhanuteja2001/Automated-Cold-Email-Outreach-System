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

class SendsoonEmail:    
    @staticmethod
    def recruiter_all_records():
        sheet = client.open("RecruiterEmailList").worksheet("Sendsoon")
        python_sheet = sheet.get_values("A:M")
        filtered_records = [row for row in python_sheet[1:] if row[4] != "Email Sent" and row[0] and row[12] != 'Email Re-sent'] 

        pp = pprint.PrettyPrinter()
        if filtered_records:
            random_record = random.choice(filtered_records)
            print("Selected a random record")
            return random_record
        return None

    def follow_up_email_all_records():
        sheet = client.open("RecruiterEmailList").worksheet("Sendsoon")
        python_sheet = sheet.get_values("A:M")
        # Define CST timezone (UTC-6)
        cst = datetime.timezone(datetime.timedelta(hours=-6))

        def parse_timestamp(timestamp_str):
            """
            Parse a timestamp string into a datetime object.
            Handles two formats:
            1. "2025-03-03 05:32:12 CST"
            2. "03/03/2025 14:16:57"
            """
            try:
                # Try parsing the first format: "2025-03-03 05:32:12 CST"
                return datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S %Z")
            except ValueError:
                try:
                    # Try parsing the second format: "03/03/2025 14:16:57"
                    return datetime.datetime.strptime(timestamp_str, "%m/%d/%Y %H:%M:%S")
                except ValueError:
                    # If neither format works, return None
                    return None

        # Filter records
        filtered_records = [
            row for row in python_sheet[1:]  # Skip the header row
            if row[4] == "Email Sent"  # Check if "Email Sent" is in the 5th column
            and row[0]  # Check if the first column is not empty
            and row[12] == 'Email Re-sent'  # Check if the 13th column is not "Email Re-sent"
            #and parse_timestamp(row[11])  # Ensure the timestamp is valid
            and (datetime.datetime.now(cst) - parse_timestamp(row[11])) >= datetime.timedelta(days=7)  # Check if the timestamp is at least 7 days old
        ]

        # Pretty printer for debugging
        pp = pprint.PrettyPrinter()

        # Return a random record if filtered_records is not empty
        if filtered_records:
            random_record = random.choice(filtered_records)
            print("Selected a random record:")
            pp.pprint(random_record)
            return random_record
        else:
            print("No records match the criteria.")
            pp.pprint(random_record)
            return None


    @staticmethod
    def update_status(people):
        sheet = client.open("RecruiterEmailList").worksheet("Sendsoon")

        for person in people:
            if person and "ID" in person:
                id_to_update = person["ID"]
                status = "Email Sent"
                resend_status = 'Waiting'
                cell = sheet.find(str(id_to_update))
                cst = pytz.timezone('US/Central')
                cst_time = datetime.datetime.now(cst)
                timestamp = cst_time.strftime("%Y-%m-%d %H:%M:%S %Z")

                if cell:
                    sheet.update_cell(cell.row, 5, status)  # E column for Status
                    sheet.update_cell(cell.row, 7, timestamp)  # G column for Timestamp
                    sheet.update_cell(cell.row, 12, resend_status) # M column for resend_status

    @staticmethod
    def update_resend_status(people):
        sheet = client.open("RecruiterEmailList").worksheet("Sendsoon")

        for person in people:
            if person and "ID" in person:
                id_to_update = person["ID"]
                resend_status = 'Email Re-sent'
                cell = sheet.find(str(id_to_update))
                cst = pytz.timezone('US/Central')
                cst_time = datetime.datetime.now(cst)
                timestamp = cst_time.strftime("%Y-%m-%d %H:%M:%S %Z")

                if cell:
                    sheet.update_cell(cell.row, 11, timestamp)  # L column for Resend_Timestamp
                    sheet.update_cell(cell.row, 12, resend_status) # M column for resend_status
              