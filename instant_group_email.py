from sheets import RecruiterDataFetch
import instant_email
import os
import smtplib
import pytz
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from bcc_handler import handle_bcc
import time

def send_group_instant_email():
    company_name = instant_email.get_input("Enter the company name: ")
    designation = instant_email.get_type()
    role = instant_email.get_input("Enter the title you are applying for with the jobid if present!")

    filtered_records = RecruiterDataFetch.get_all_records_by_company(company_name, designation)
    
    if filtered_records:

        print("Enter the dynamic points for the email:")
        dynamic_points = instant_email.get_dynamic_points()

        server = smtplib.SMTP("smtp.gmail.com:587")
        server.ehlo()
        server.starttls()
        
        try:
            server.login(os.environ["gmail_email"], os.environ["gmail_password"])
            print("Logged in successfully.")


            for person in filtered_records:
                print(f"sending email to {person[1]} from {person[3]} who is a {designation}")
                if person and person[1] and person[3]:
                    name_parts = person[1].split()
                    
                    if len(name_parts) == 1:
                        first_name = name_parts[0]
                        main_email = person[2]
                        bcc_emails = None
                    else:
                        first_name = name_parts[0]
                        last_name = name_parts[-1]
                        if person[2]:
                            main_email = person[2]
                            # Use bcc_handler to get potential BCC emails
                            _, bcc_emails, _ = handle_bcc(f"{first_name} {last_name}", person[3], None)
                        else:
                            main_email, bcc_emails, _ = handle_bcc(f"{first_name} {last_name}", person[3], None)

                    company = person[3]
                    type_ = person[5]
                
                    try:
                        # Replace with actual parameters
                        instant_mail = instant_email.InstantColdMail(first_name, main_email, company, designation, server, dynamic_points, role, bcc=bcc_emails)
                        
                        cst = pytz.timezone('US/Central')
                        cst_time = datetime.datetime.now(cst)
                        timestamp = cst_time.strftime("%Y-%m-%d %H:%M:%S %Z")

                        # Log successful transaction
                        transaction_entry = [
                            timestamp,
                            company,
                            person[1],
                            main_email,
                            "Email Sent",
                            role,
                            "Instant Group Send",
                            bcc_emails
                        ]

                        RecruiterDataFetch.add_transaction(transaction_entry)
                    
                        person[6] = timestamp
                        person[4] = "Email Sent"
                        person[7] = "No Priority"  # Reset priority after sending

                        print("updating the email status")
                        RecruiterDataFetch.update_email_status_instant(person)

                        print(f"Transaction added for {person[1]} from {company}")
                        time.sleep(30)

                    except Exception as email_error:
                        print(f"Failed to send email: {email_error}")

                        # Log failed transaction
                        cst = pytz.timezone('US/Central')
                        cst_time = datetime.datetime.now(cst)
                        timestamp = cst_time.strftime("%Y-%m-%d %H:%M:%S %Z")

                        failure_entry = [
                            timestamp,
                            company,
                            person[1],
                            main_email,
                            "Email Failed",
                            role,
                            "Instant Group Send",
                            bcc_emails,
                            str(email_error)  # Include error message
                        ]
                        RecruiterDataFetch.add_transaction(failure_entry)
                        print(f"Failure transaction logged for {person[1]} from {company}")

        finally:
            server.quit()
            print("SMTP server connection closed.")
    else:

        print("No records found!!")

if __name__ == "__main__":
    send_group_instant_email()




