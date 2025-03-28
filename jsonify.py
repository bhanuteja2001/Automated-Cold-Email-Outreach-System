import json
from sheets import RecruiterDataFetch, SendsoonEmail

class RecruiterDataProcessor:
    def __init__(self):
        self.raw_data = RecruiterDataFetch.recruiter_all_records()
        self.headers = ["ID", "Name", "Email", "Company", "Status", "Type", "Timestamp", "Priority"]
        self.data = []

    def process_data(self):
        if self.raw_data:
            self.data.append(dict(zip(self.headers, self.raw_data)))

    def get_json_data(self):
        if not self.data:
            self.process_data()
        return json.dumps(self.data, indent=2)

    @classmethod
    def get_processed_json(cls):
        processor = cls()
        return processor.get_json_data()

class RecruiterDataProcessor_SendSoon:
    def __init__(self):
        self.raw_data = SendsoonEmail.recruiter_all_records()
        self.headers = ["ID", "Name", "Email", "Company", "Status", "Position", "Timestamp_of_delivery", "Job_position", "Timestamp_row_addition", "Resume_URL", "Dynamic_points", "Resend_Timestamp", "Resend_Status"]
        self.data = []

    def process_data(self):
        if self.raw_data:
            self.data.append(dict(zip(self.headers, self.raw_data)))

    def get_json_data(self):
        if not self.data:
            self.process_data()
        return json.dumps(self.data, indent=2)

    @classmethod
    def get_processed_json(cls):
        processor = cls()
        return processor.get_json_data()

class RecruiterDataProcessor_Re_SendSoon:
    def __init__(self):
        self.raw_data = SendsoonEmail.follow_up_email_all_records()
        self.headers = ["ID", "Name", "Email", "Company", "Status", "Position", "Timestamp_of_delivery", "Job_position", "Timestamp_row_addition", "Resume_URL", "Dynamic_points", "Resend_Timestamp", "Resend_Status"]
        self.data = []

    def process_data(self):
        if self.raw_data:
            self.data.append(dict(zip(self.headers, self.raw_data)))

    def get_json_data(self):
        if not self.data:
            self.process_data()
        return json.dumps(self.data, indent=2)

    @classmethod
    def get_processed_json(cls):
        processor = cls()
        return processor.get_json_data()
    
if __name__ == "__main__":
    # Example usage
    try:
        json_output = RecruiterDataProcessor_Re_SendSoon.get_processed_json()
        print(json_output)
    except Exception as e:
        print(f"An error occurred: {e}")