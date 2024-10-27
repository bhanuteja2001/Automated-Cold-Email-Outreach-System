# Automated Cold Email Outreach System



# Cold Email Automation Project

## Overview

This project automates the process of sending cold emails for job applications using Google Sheets for data management and GitHub Actions for scheduling. It streamlines the outreach process for job seekers targeting Data Engineer Directors, Managers, Recruiters, and other relevant professionals.

## Features

- **Google Sheets Integration**: Uses Google Sheets API to access and update contact information and email status.
- **Automated Email Sending**: Sends personalized emails with pre-drafted content and attached resumes.
- **Scheduled Execution**: Utilizes GitHub Actions to schedule and run the email sending script at specified intervals.
- **Status Tracking**: Automatically updates the Google Sheet with the current status of each email (sent or pending).
- **Cloud Development**: Developed using GitHub Codespaces for a consistent and portable development environment.

## Technology Stack

- Python
- Google Sheets API
- GitHub Actions
- GitHub Codespaces

## Setup

1. **Google Sheets Setup**:
   - Create a Google Sheet with columns for contact information (name, email, position, company, etc.) and email status.
   - Set up Google Cloud Project and enable Google Sheets API.
   - Generate credentials (JSON key file) for accessing the Google Sheets API.

2. **GitHub Repository**:
   - Create a new repository for this project.
   - Store the Google Sheets API credentials securely as GitHub Secrets.

3. **Email Template**:
   - Prepare email drafts and resume files to be used in the automation.

4. **Python Script**:
   - Develop a Python script that:
     - Authenticates with Google Sheets API
     - Reads contact information from the sheet
     - Composes and sends emails
     - Updates the sheet with email status

5. **GitHub Actions**:
   - Create a workflow file (e.g., `.github/workflows/send-emails.yml`) to schedule the script execution.

## Usage

1. Update the Google Sheet with new contacts as needed.
2. The GitHub Action will run on the scheduled time, sending emails to contacts marked as 'pending'.
3. Check the Google Sheet for updated email statuses and any responses received.

## Privacy and Security

- Ensure all credentials and sensitive information are stored securely as GitHub Secrets.
- Comply with all relevant email and privacy regulations in your jurisdiction.
- Use your college email responsibly and in accordance with institutional policies.

## Maintenance

- Regularly update the email templates and resume attachments as needed.
- Monitor the GitHub Actions logs for any execution issues.
- Periodically review and refine the contact list in the Google Sheet.

---
