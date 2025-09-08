import os
import smtplib
import pytz
import datetime
import time
from sheets import RecruiterDataFetch
from coldmail import ColdMail

def should_send_email():
    now = datetime.datetime.now(pytz.timezone('US/Central'))
    day = now.weekday()
    hour = now.hour

    if day in [5, 6]:  # Weekend
        return False
    elif day == 0 and hour < 8:  # Monday before 8 AM
        return True
    elif day in [1, 2, 3]:  # Tuesday, Wednesday, Thursday
        return True
    elif day == 4 and hour < 8:  # Friday before 8 AM
        return True
    return False

def prioritize_emails(emails):
    high_priority = []
    medium_priority = []

    for email in emails:
        if email[7] == 'High':
            high_priority.append(email)
        elif email[7] == 'Medium':
            medium_priority.append(email)

    return high_priority + medium_priority

def process_queue():
    if not should_send_email():
        print("Not the right time to send emails. Exiting.")
        return

    priority_emails = RecruiterDataFetch.fetch_priority_emails()
    
    if not priority_emails:
        print("No priority emails to send.")
        return

    prioritized_emails = prioritize_emails(priority_emails)

    server = smtplib.SMTP("smtp.gmail.com:587")
    server.ehlo()
    server.starttls()
    email = os.environ["gmail_email"] # os.getenv("gmail_email")
    pss = os.environ["gmail_password"] # os.getenv("gmail_password")
    server.login(email, pss)
    #server.login(os.environ["gmail_email"], os.environ["gmail_password"])

    max_emails = int(os.environ.get("MAX_EMAILS_PER_RUN", 10))
    emails_to_send = prioritized_emails[:max_emails]

    for email in emails_to_send:
        print("Email sending to ", email[1].split(" ")[0])
        try:
            ColdMail(email[1].split()[0], email[2], email[3], email[5], server, priority=email[7])
            
            RecruiterDataFetch.update_email_status({
                "ID": email[0],
                "Status": "Email Sent",
                "Priority": "No Priority",
                "Timestamp": datetime.datetime.now(pytz.timezone('US/Central')).strftime("%Y-%m-%d %H:%M:%S %Z")
            })

            try:

                timestamp = datetime.datetime.now(pytz.timezone('US/Central')).strftime("%Y-%m-%d %H:%M:%S %Z")
                # Prepare the transaction entry
                Transaction_entry = [
                    timestamp,
                    email[3],
                    email[1],
                    email[2],
                    "Email Sent",
                    email[5],
                    email[7]
                ]
                
                # Add the transaction
                RecruiterDataFetch.add_transaction(Transaction_entry)
                print(f"Transaction added for {email[1]} from {email[3]}")

            except KeyError as e:
                # Handle missing keys in the 'person' dictionary
                print(f"Missing key in person data: {e}")

            except Exception as e:
                # Handle any other exceptions that might occur
                print(f"Failed to add transaction: {e}")


            
            print(f"Email sent to {email[2]} and status updated.")
            time.sleep(30)  # 30-second delay between emails
        except Exception as e:
            print(f"Failed to send email to {email[2]}: {str(e)}")

    server.quit()

if __name__ == "__main__":
    process_queue()