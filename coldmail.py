import smtplib
import os
import json
import datetime
import pytz
from bcc_handler import handle_bcc
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from jsonify import RecruiterDataProcessor
from sheets import RecruiterDataFetch

class ColdMail:
    def __init__(self, Name, Email, Company, Type, server, bcc=None, priority=None):
        self.server = server
        self.FROM = os.environ["gmail_email"]
        self.TO = [Email] if isinstance(Email, str) else Email
        self.BCC = bcc if isinstance(bcc, list) else [bcc] if bcc else []
        self.priority = priority

        # Initialize subject and content
        subject = ""
        content = "."

        # Prepare the email content and subject based on the Type
        if Type == "DE_Manager" or Type == "Director DE":
            with open("Content/manager_DE.txt", "r") as file:
                content = file.read()
            content = content.format(Name=Name, Company=Company)
            subject = f"Expressing Interest in Data opportunities at {Company}"
            resume_file = "Resumes/DE/Bhanu_Kurakula_Resume.pdf"

        elif Type == "DS_Manager":
            with open("Content/manager_DS.txt", "r") as file:
                content = file.read()
            content = content.format(Name=Name, Company=Company)
            subject = f"Expressing Interest in Data opportunities at {Company}"
            resume_file = "Resumes/DS/Bhanu_Kurakula_Resume.pdf"
        
        elif Type == "Team_Member":
            with open("Content/Team_Member.html", "r") as file:
                content = file.read()
            content = content.format(Name=Name, Company=Company)
            subject = f"Expressing Interest in Data opportunities at {Company}"
            resume_file = "Resumes/DE/Bhanu_Kurakula_Resume.pdf"


        elif Type == "Recruiter":
            with open("Content/Recruiter.txt", "r") as file:
                content = file.read()
            content = content.format(Name=Name, Company=Company)
            subject = f"Expressing Interest in Data opportunities at {Company}"
            resume_file = "Resumes/Recruiter/Bhanu_Kurakula_Resume.pdf"
        
        else:
            print(f"Unknown Type: {Type}. Email will not be sent.")
            return

        # Create the email message
        self.msg = MIMEMultipart()
        self.msg["From"] = self.FROM
        self.msg["To"] = ", ".join(self.TO)
        self.msg["Subject"] = subject

        # Attach the email body
        self.msg.attach(MIMEText(content, "html"))

        # Attach the appropriate resume file if it exists
        if "resume_file" in locals():
            self.attach_resume(resume_file)
            # Send the email only if the resume file exists
            self.send_mail()
        else:
            print(f"No valid resume file for Type: {Type}. Email will not be sent.")

    def attach_resume(self, resume_file):
        # Attach the specified resume file
        with open(resume_file, "rb") as resume:
            part = MIMEApplication(resume.read(), Name=os.path.basename(resume_file))
            part["Content-Disposition"] = (
                f'attachment; filename="{os.path.basename(resume_file)}"'
            )
            self.msg.attach(part)

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
    server.login(os.environ["gmail_email"], os.environ["gmail_password"])

    processor = RecruiterDataProcessor()
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
                coldmail = ColdMail(
                    first_name,
                    main_email,
                    person["Company"],
                    person["Type"],
                    server,
                    bcc=bcc_emails,
                    priority=person.get("Priority", "No Priority")
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
                        person["Type"],
                        person.get("Priority", "No Priority"),
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


            person["Timestamp"] = timestamp
            person["Status"] = "Email Sent"
            person["Priority"] = "No Priority"  # Reset priority after sending

    RecruiterDataFetch.update_status(people)

    server.quit()
