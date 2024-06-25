import requests
from bs4 import BeautifulSoup
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Email credentials and settings from environment variables
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
TO_ADDRESS = os.getenv('TO_ADDRESS')

url = "https://employment.ucsd.edu/jobs?page_size=100&page_number=1&keyword=hpc&sort_by=score&sort_order=DESC"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
item_titles = soup.find_all('a', class_='item-title')
found_jobs = {a.get_text(strip=True): a['href'] for a in item_titles}

# Check if the .txt file exists
file_path = 'job_listings.txt'
if os.path.exists(file_path):
    with open(file_path, 'r') as file:
        existing_jobs = {line.split(', Href: ')[0].replace('Text: ', '') for line in file.readlines()}
else:
    existing_jobs = set()

# Find new jobs that aren't in the existing jobs
found_job_titles = set(found_jobs.keys())
added_jobs = found_job_titles - existing_jobs

# Print 'hello' if there are new jobs
if added_jobs:
    # Create the email content
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_ADDRESS
    msg['Subject'] = 'New Job Listings'
    body = "\n".join([f"Text: {title}, Href: {found_jobs[title]}" for title in new_jobs])
    msg.attach(MIMEText(body, 'plain'))

    # Connect to the SMTP server and send the email
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, TO_ADDRESS, msg.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Append the new jobs to the .txt file
with open(file_path, 'a') as file:
    for title in added_jobs:
        file.write(f"Text: {title}, Href: {found_jobs[title]}\n")