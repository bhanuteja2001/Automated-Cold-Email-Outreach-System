import smtplib
import os
import json
import datetime
import pytz
import requests
from bcc_handler import handle_bcc
from urllib.parse import urlparse, parse_qs
from jsonify import RecruiterDataProcessor_SendSoon
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from sheets import RecruiterDataFetch, SendsoonEmail
from dotenv import load_dotenv

load_dotenv()


class Sendsoon:
    def __init__(self, Name, Email, Company, Position, Job_position, Resume_URL, Dynamic_points, server, bcc=None):
        self.server = server
        self.FROM = os.environ["gmail_email"]
        self.TO = [Email] if isinstance(Email, str) else Email
        self.BCC = bcc if isinstance(bcc, list) else [bcc] if bcc else []
        self.Job_position = Job_position
        self.Resume_URL = Resume_URL
        self.Dynamic_points = Dynamic_points

        # Initialize subject and content
        subject = ""
        content = "."

        ### IF DYNAMIC POINTS ARE NOT PRESENT, DEFAULT IS NOT ENABLED YET!
        ## Need to draft perfect emails for all roles, for now only recruiter is good!
        def get_template_file(Position):
            template_map = {
                "DE_Manager": "Content/sendsoon/DE_Manager.html",
                "Director DE": "Content/sendsoon/Director_DE_Manager.html",
                "DS_Manager": "Content/sendsoon/DE_Manager.html",
                "Recruiter": "Content/sendsoon/recruiter.html",
                "Team_Member": "Content/sendsoon/team_member.html"
            }
            return template_map.get(Position, "Content/default_template.html")
        
        template_file = get_template_file(Position)        

        # Prepare the email content and subject based on the Position
        if Position in ["DE_Manager", "Director DE"]:
            resume_file = "Resumes/DE/Bhanu_Kurakula_Resume.pdf"
        elif Position == "DS_Manager":
            resume_file = "Resumes/DS/Bhanu_Kurakula_Resume.pdf"
        elif Position == "Team_Member":
            resume_file = "Resumes/DE/Bhanu_Kurakula_Resume.pdf"
        elif Position == "Recruiter":
            resume_file = "Resumes/Recruiter/Bhanu_Kurakula_Resume.pdf"
        else:
            print(f"Unknown Position: {Position}. Email will not be sent.")
            return

        # Check if Resume_URL is provided
        if self.Resume_URL:
            # Download the Google Doc and use it as the resume file
            resume_file = self.download_doc(self.Resume_URL)
            if not resume_file:
                print("Failed to download the resume from the provided URL. Using default resume.")
                resume_file = "Resumes/DE/Bhanu_Kurakula_Resume.pdf"  # Fallback to default
        else:
            # Use the default resume file
            if not os.path.exists(resume_file):
                print(f"Resume file not found: {resume_file}. Email will not be sent.")
                return

        # Read the template file and format the content
        try:
            with open(template_file, "r") as file:
                content = file.read()
            content = content.format(Name=Name, Company=Company, DynamicPoints=Dynamic_points, role=Job_position)
            subject = f"Expressing interest in the {Job_position} position: Bhanu Kurakula"
        except Exception as e:
            print(f"Failed to read or format template file: {e}")
            return

        # Create the email message
        self.msg = MIMEMultipart()
        self.msg["From"] = self.FROM
        self.msg["To"] = ", ".join(self.TO)
        self.msg["Subject"] = subject

        # Attach the email body
        self.msg.attach(MIMEText(content, "html"))

        # Attach the resume file
        self.attach_resume(resume_file)

        # Send the email
        self.send_mail()

    def download_doc(self, Resume_URL):
        # Extract doc_id
        parsed_url = urlparse(Resume_URL)
        path_segments = parsed_url.path.split('/')
        
        if 'd' in path_segments:
            doc_id_index = path_segments.index('d') + 1
            if doc_id_index < len(path_segments):
                doc_id = path_segments[doc_id_index]
            else:
                print("Invalid Google Docs URL.")
                return None
        else:
            query_params = parse_qs(parsed_url.query)
            if 'id' in query_params:
                doc_id = query_params['id'][0]
            else:
                print("Invalid Google Docs URL.")
                return None

        # Construct the export URL
        export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=pdf"
        
        # Send a GET request to download the file
        response = requests.get(export_url)
        output_filename = 'Bhanu_Kurakula_Resume.pdf'
        
        # Check if the request was successful
        if response.status_code == 200:
            with open(output_filename, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded {output_filename}")
            return output_filename
        else:
            print(f"Failed to download. Status code: {response.status_code}")
            return None
    
    def attach_resume(self, resume_file):
        try:
            with open(resume_file, "rb") as resume:
                part = MIMEApplication(resume.read(), Name=os.path.basename(resume_file))
                part["Content-Disposition"] = f'attachment; filename="{os.path.basename(resume_file)}"'
                self.msg.attach(part)
            print(f"Resume attached: {resume_file}")
        except Exception as e:
            print(f"Failed to attach resume: {e}")

    def send_mail(self):
        try:
            # Combine all recipients for sending
            all_recipients = self.TO + self.BCC
            
            # Send the email
            self.server.sendmail(self.FROM, all_recipients, self.msg.as_string())
            
            # Log the send (but don't reveal BCC recipients in the log)
            print(f"Email sent to {self.TO} (BCC recipients not shown)")
        except Exception as e:
            print(f"Failed to send email: {e}")
        

if __name__ == "__main__":
    # Run the script
    server = smtplib.SMTP("smtp.gmail.com:587")
    server.ehlo()
    server.starttls()
    email = os.environ["gmail_email"] # os.getenv("gmail_email")
    pss = os.environ["gmail_password"] # os.getenv("gmail_password")
    server.login(email, pss)

    processor = RecruiterDataProcessor_SendSoon()
    people = json.loads(processor.get_json_data())

    for person in people:
        if person and "Name" in person and "Company" in person:
            name_parts = person["Name"].split()
            
            if len(name_parts) == 1:
                first_name = name_parts[0]
                main_email = person.get("Email")
                bcc_emails = None
            else:
                first_name = name_parts[0]
                last_name = name_parts[-1]
                if person.get("Email"):
                    main_email = person["Email"]
                    # Use bcc_handler to get potential BCC emails
                    _, bcc_emails, _ = handle_bcc(f"{first_name} {last_name}", person["Company"], None)
                else:
                    main_email, bcc_emails, _ = handle_bcc(f"{first_name} {last_name}", person["Company"], None)
            
            if main_email:
                print(f"Sending email to {first_name} at {main_email}")
                sendmail = Sendsoon(
                    first_name,
                    main_email,
                    person["Company"],
                    person["Position"],
                    person["Job_position"],
                    person["Resume_URL"],
                    person["Dynamic_points"],
                    server,
                    bcc=bcc_emails
                )

            cst = pytz.timezone('US/Central')
            cst_time = datetime.datetime.now(cst)
            timestamp = cst_time.strftime("%Y-%m-%d %H:%M:%S %Z")
            
            try:
                # Prepare the transaction entry
                Transaction_entry = [
                        timestamp,
                        person["Company"],
                        person["Name"],
                        person["Email"],
                        "Email Sent",
                        person["Position"],
                        "sendsoon",
                        ", ".join(bcc_emails) if bcc_emails else ""  # Convert list to string
                    ]

                print(Transaction_entry)
                
                # Add the transaction
                RecruiterDataFetch.add_transaction(Transaction_entry)
                print(f"Transaction added for {person['Name']} from {person['Company']}")

            except KeyError as e:
                # Handle missing keys in the 'person' dictionary
                print(f"Missing key in person data: {e}")

            except Exception as e:
                # Handle any other exceptions that might occur
                print(f"Failed to add transaction: {e}")

            # Update status
            person["Status"] = "Email Sent"

    SendsoonEmail.update_status(people)

    server.quit()