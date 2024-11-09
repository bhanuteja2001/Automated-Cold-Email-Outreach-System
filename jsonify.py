import json
from sheets import RecruiterDataFetch


class RecruiterDataProcessor:
    def __init__(self):
        self.raw_data = RecruiterDataFetch.recruiter_all_records()
        self.headers = ["ID", "Name", "Email", "Company", "Status", "Type", "Timestamp"]
        self.data = []

    def process_data(self):
        # Since we are now assuming self.raw_data does not contain headers,
        # we can directly map the rows to the headers.
        if self.raw_data:
            self.data.append(
                dict(zip(self.headers, self.raw_data))
            )  # Assigning the single random record to headers

    def get_json_data(self):
        if not self.data:
            self.process_data()
        return json.dumps(self.data, indent=2)

    @classmethod
    def get_processed_json(cls):
        processor = cls()
        return processor.get_json_data()
