import os
import smtplib
import pytz
import datetime
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

def get_dynamic_points():
    points = []
    while True:
        point = input("Enter a point (or press Enter to finish): ").strip()
        if not point:
            break
        points.append(point)
    return points

def get_yes_no_input(prompt):
    while True:
        print(prompt)
        print("1. Yes")
        print("2. No")
        choice = input("Enter your choice (1 or 2): ").strip()
        if choice == '1':
            return True
        elif choice == '2':
            return False
        else:
            print("Invalid input. Please enter 1 or 2.")

class InstantColdMail:
    def __init__(self, Name, Email, Company, Type, server, dynamic_points, bcc=None):
        self.server = server
        self.bcc = bcc if isinstance(bcc, list) else [bcc] if bcc else []

        # Select the appropriate email template based on Type
        template_file = self.get_template_file(Type)
        
        # Read the email template
        with open(template_file, "r") as file:
            content = file.read()

        # Format the dynamic points
        points_html = "\n".join([f"<li>{point}</li>" for point in dynamic_points])
        
        # Replace placeholders in the template
        content = content.format(Name=Name, Company=Company, DynamicPoints=points_html)
        
        # Set subject and resume file based on Type
        subject, resume_file = self.get_subject_and_resume(Type, Company)

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

        # Attach the resume
        self.attach_resume(resume_file)
        self.send_mail()

    def get_template_file(self, Type):
        template_map = {
            "DE_Manager": "Content/manager_DE.html",
            "Director DE": "Content/director_DE.html",
            "DS_Manager": "Content/manager_DS.html",
            "Recruiter": "Content/Recruiter.html"
        }
        return template_map.get(Type, "Content/default_template.html")

    def get_subject_and_resume(self, Type, Company):
        if Type == "DE_Manager" or Type == "Director DE":
            subject = f"Info on Data Engineering opportunities at {Company}"
            resume_file = "Resumes/Bhanu_Kurakula_DE_Resume.pdf"
        elif Type == "DS_Manager":
            subject = f"Info on Data Science opportunities at {Company}"
            resume_file = "Resumes/Bhanu_DS_Resume.pdf"
        elif Type == "Recruiter":
            subject = f"Inquiry About Full-Time Opportunities at {Company}"
            resume_file = "Resumes/Bhanu_Kurakula_Resume.pdf"
        else:
            subject = f"Inquiry about opportunities at {Company}"
            resume_file = "Resumes/Bhanu_Kurakula_Resume.pdf"
        return subject, resume_file

    def attach_resume(self, resume_file):
        with open(resume_file, "rb") as resume:
            part = MIMEApplication(resume.read(), Name=os.path.basename(resume_file))
            part["Content-Disposition"] = f'attachment; filename="{os.path.basename(resume_file)}"'
            self.msg.attach(part)

    def send_mail(self):
        try:
            all_recipients = self.TO + self.BCC
            self.server.sendmail(self.FROM, all_recipients, self.msg.as_string())
            print(f"Email sent to {self.TO} (BCC recipients not shown)")
        except Exception as e:
            print(f"Failed to send email: {e}")

def send_instant_email():
    name = get_input("Enter Name (Full Name or First Name): ")
    email = get_input("Enter Email: ")
    company = get_input("Enter Company Name: ")
    type_ = get_type()

    use_bcc = get_yes_no_input("Do you want to use BCC?")

    name_parts = name.split()
    if len(name_parts) == 1:
        first_name = name_parts[0]
        last_name = ""
    else:
        first_name = name_parts[0]
        last_name = name_parts[-1]

    main_email = email
    bcc_emails = None

    if use_bcc:
        if email:
            main_email = email
            _, bcc_emails, _ = handle_bcc(f"{first_name} {last_name}", company, None)
        else:
            main_email, bcc_emails, _ = handle_bcc(f"{first_name} {last_name}", company, None)

    if not main_email:
        print("Unable to generate a valid email. Aborting.")
        return

    print("Enter the dynamic points for the email:")
    dynamic_points = get_dynamic_points()

    server = smtplib.SMTP("smtp.gmail.com:587")
    server.ehlo()
    server.starttls()
    try:
        server.login(os.environ["gmail_email"], os.environ["gmail_password"])
        print("Logged in successfully.")

        try:
            # Replace with actual parameters
            instant_mail = InstantColdMail(first_name, main_email, company, type_, server, dynamic_points, bcc=bcc_emails)
            
            cst = pytz.timezone('US/Central')
            cst_time = datetime.datetime.now(cst)
            timestamp = cst_time.strftime("%Y-%m-%d %H:%M:%S %Z")

            # Log successful transaction
            transaction_entry = [
                timestamp,
                company,
                name,
                main_email,
                "Email Sent",
                type_,
                "Instant Send",
                bcc_emails
            ]
            RecruiterDataFetch.add_transaction(transaction_entry)
            print(f"Transaction added for {name} from {company}")

            # Add new entry to Google Sheets
            new_entry = [
                "",  # ID will be auto-generated
                name,
                main_email,
                company,
                "Email Sent",
                type_,
                timestamp,
                "No Priority"  # Assuming default priority
            ]
            RecruiterDataFetch.add_new_entry(new_entry)
            print(f"Entry for {name} and {company} added to Google Sheet-1")

        except Exception as email_error:
            print(f"Failed to send email: {email_error}")

            # Log failed transaction
            cst = pytz.timezone('US/Central')
            cst_time = datetime.datetime.now(cst)
            timestamp = cst_time.strftime("%Y-%m-%d %H:%M:%S %Z")

            failure_entry = [
                timestamp,
                company,
                name,
                main_email,
                "Email Failed",
                type_,
                "Instant Send",
                bcc_emails,
                str(email_error)  # Include error message
            ]
            RecruiterDataFetch.add_transaction(failure_entry)
            print(f"Failure transaction logged for {name} from {company}")

    finally:
        server.quit()
        print("SMTP server connection closed.")

if __name__ == "__main__":
    send_instant_email()