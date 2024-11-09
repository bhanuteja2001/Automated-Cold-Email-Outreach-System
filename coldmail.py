import smtplib
import os
import json
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from jsonify import RecruiterDataProcessor
from sheets import RecruiterDataFetch


class ColdMail:
    def __init__(self, Name, Email, Company, Type, server):
        self.server = server  # Store server instance

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

            # Format the content with placeholders
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
        self.FROM = os.environ["gmail_email"]
        self.TO = [Email]

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
            self.server.sendmail(self.FROM, self.TO, self.msg.as_string())
            print(f"Email sent to {self.TO}")
        except Exception as e:
            print(f"Failed to send email to {self.TO}: {e}")


if __name__ == "__main__":
    # Run the script
    server = smtplib.SMTP("smtp.gmail.com:587")
    server.ehlo()
    server.starttls()
    server.login(os.environ["gmail_email"], os.environ["gmail_password"])

    processor = RecruiterDataProcessor()
    people = json.loads(processor.get_json_data())
    print("Cold_Email.py received {} records".format(len(people)))

    # Go through each recruiter, taking the name, company, and email
    for person in people:
        if (
            person
            and "Name" in person
            and "Email" in person
            and "Company" in person
            and "Type" in person
        ):
            print(
                "Sending email to {} from {} who is the {}".format(
                    person["Name"], person["Company"], person["Type"]
                )
            )
            coldmail = ColdMail(
                person["Name"],
                person["Email"],
                person["Company"],
                person["Type"],
                server,
            )
            person["Status"] = "Email Sent"
            person["Timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    RecruiterDataFetch.update_status(people)

    server.quit()
