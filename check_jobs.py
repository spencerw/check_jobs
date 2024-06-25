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
found_jobs = {a.get_text(strip=True): "https://employment.ucsd.edu" + a['href'] for a in item_titles}

# Check if the .txt file exists
file_path = 'job_listings.txt'
if os.path.exists(file_path):
    with open(file_path, 'r') as file:
        print('found existing job_listings.txt file')
        existing_jobs = {line.split(', Href: ')[0].replace('Text: ', '') for line in file.readlines()}
else:
    print(file_path + ' not found, creating new file')
    existing_jobs = set()

print('Found ' + str(len(existing_jobs)) + ' existing jobs')

# Find new jobs that aren't in the existing jobs
found_job_titles = set(found_jobs.keys())
added_jobs = found_job_titles - existing_jobs

print('Found ' + str(len(added_jobs)) + ' new jobs')

# Send an email if there are any new jobs
if added_jobs:
    # Create the email content
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_ADDRESS
    msg['Subject'] = 'New UCSD HPC Jobs'
    body = ''
    for title in added_jobs:
        job_url = found_jobs[title]
        body += f"<p><a href='{job_url}'>{title}</a></p>"
    msg.attach(MIMEText(body, 'html'))

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
    print('Writing ' + str(len(added_jobs)) + ' jobs to ' + file_path)
    for title in added_jobs:
        file.write(f"Text: {title}, Href: {found_jobs[title]}\n")