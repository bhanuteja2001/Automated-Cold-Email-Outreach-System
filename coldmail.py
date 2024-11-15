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
    def __init__(self, Name, Email, Company, Type, server, bcc=None):
        self.server = server
        self.FROM = os.environ["gmail_email"]
        self.TO = [Email] if isinstance(Email, str) else Email
        self.BCC = bcc if isinstance(bcc, list) else [bcc] if bcc else []


        # Initialize subject and content
        subject = "Default Subject"
        content = "Default content. Please check the email type."

        # Prepare the email content and subject based on the Type
        if Type == "DE_Manager" or Type == "Director DE":
            with open("Content/manager_DE.txt", "r") as file:
                content = file.read()
            content = content.format(Name=Name, Company=Company)
            subject = f"Info on Data Engineering opportunities at {Company}"
            resume_file = "Resumes/Bhanu_DE_Resume.pdf"
        elif Type == "DS_Manager":
            with open("Content/manager_DS.txt", "r") as file:
                content = file.read()
            content = content.format(Name=Name, Company=Company)
            subject = f"Info on Data Science opportunities at {Company}"
            resume_file = "Resumes/Bhanu_DS_Resume.pdf"
        elif Type == "Recruiter":
            with open("Content/Recruiter.txt", "r") as file:
                content = file.read()
            content = content.format(Name=Name, Company=Company)
            subject = f"Info on 2025 New Grad / Spring opportunities at {Company}"
            resume_file = "Resumes/Bhanu_Kurakula_Resume.pdf"
        else:
            print(f"Unknown Type: {Type}. Email will not be sent.")
            return  # Exit the constructor if Type is unknown

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
    #print("Cold_Email.py received {} records".format(len(people)))

    # Go through each recruiter, taking the name, company, and email
    for person in people:
        if person and "Name" in person and "Company" in person:
            name_parts = person["Name"].split()
            
            if len(name_parts) == 1:
                # If only first name is given
                first_name = name_parts[0]
                main_email = person.get("Email")
                bcc_emails = None
            else:
                # If full name is given
                first_name = name_parts[0]
                last_name = name_parts[-1]
                if person.get("Email"):
                    main_email = person["Email"]
                    # Use bcc_handler to get potential BCC emails
                    _, bcc_emails, _ = handle_bcc(f"{first_name} {last_name}", person["Company"], None)
                else:
                    # If no email is provided, use bcc_handler for both main and BCC emails
                    main_email, bcc_emails, _ = handle_bcc(f"{first_name} {last_name}", person["Company"], None)
            
            if main_email:
                print(f"Sending email to {first_name} at {main_email}")
                coldmail = ColdMail(
                    first_name,
                    main_email,
                    person["Company"],
                    person["Type"],
                    server,
                    bcc=bcc_emails
                )
            person["Status"] = "Email Sent"

            # Create a timezone object for CST
            cst = pytz.timezone('US/Central')
            
            # Get the current time in CST
            cst_time = datetime.datetime.now(cst)
            
            # Format the timestamp
            timestamp = cst_time.strftime("%Y-%m-%d %H:%M:%S %Z")
                
            person["Timestamp"] = timestamp

    RecruiterDataFetch.update_status(people)

    server.quit()