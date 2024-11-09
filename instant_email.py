import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from bcc_handler import handle_bcc
from sheets import RecruiterDataFetch

def get_input(prompt, optional=False):
    while True:
        value = input(prompt).strip()
        if value or optional:
            return value

def get_type():
    types = ["DE_Manager", "Director DE", "DS_Manager", "Recruiter"]
    print("Select the type:")
    for i, t in enumerate(types, 1):
        print(f"{i}. {t}")
    while True:
        try:
            choice = int(input("Enter the number: "))
            if 1 <= choice <= len(types):
                return types[choice - 1]
        except ValueError:
            pass
        print("Invalid choice. Please try again.")

class InstantColdMail:
    def __init__(self, Name, Email, Company, Type, server, bcc=None):
        self.server = server
        self.bcc = bcc if isinstance(bcc, list) else [bcc] if bcc else []

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
            return

        # Create the email message
        self.FROM = os.environ["gmail_email"]
        self.TO = [Email]
        self.BCC = self.bcc

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
            # Combine all recipients
            all_recipients = self.TO + self.BCC
            
            # Remove BCC from headers if it exists
            if 'Bcc' in self.msg:
                del self.msg['Bcc']
            
            # Send the email
            self.server.sendmail(self.FROM, all_recipients, self.msg.as_string())
            
            # Log the send (but don't reveal BCC recipients in the log)
            print(f"Email sent to {self.TO} (BCC recipients not shown)")
        except Exception as e:
            print(f"Failed to send email: {e}")

def send_instant_email():
    name = get_input("Enter Name (Full Name or First Name): ")
    email = get_input("Enter Email (optional): ", optional=True)
    company = get_input("Enter Company Name: ")
    type_ = get_type()

    main_email, bcc_emails, first_name = handle_bcc(name, company, email)

    if not main_email:
        print("Unable to generate a valid email. Aborting.")
        return

    # Set up SMTP server
    server = smtplib.SMTP("smtp.gmail.com:587")
    server.ehlo()
    server.starttls()
    server.login(os.environ["gmail_email"], os.environ["gmail_password"])

    # Send email
    try:
        instant_mail = InstantColdMail(first_name, main_email, company, type_, server, bcc=bcc_emails)
        
        # Update Google Sheet
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_entry = [
            "",  # ID will be auto-generated
            name,
            main_email,
            company,
            "Email Sent",
            type_,
            timestamp
        ]
        RecruiterDataFetch.add_new_entry(new_entry)
        print("Entry added to Google Sheet")
        
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()

if __name__ == "__main__":
    send_instant_email()