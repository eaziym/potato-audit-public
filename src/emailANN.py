from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import openpyxl
import csv


def get_previous_working_day():
    """Get the previous working day (skips weekends)"""
    today = datetime.now()
    # Monday = 0, Sunday = 6
    if today.weekday() == 0:  # Monday
        # Go back 3 days to Friday
        return today - timedelta(days=3)
    elif today.weekday() == 6:  # Sunday
        # Go back 2 days to Friday
        return today - timedelta(days=2)
    else:
        # Go back 1 day for any other day
        return today - timedelta(days=1)

def create_html_table(announcements):
    """ Convert announcements to HTML table with improved styling """
    # CSS styles
    style = """
    <style>
        table {
            border-collapse: collapse;
            width: 100%;
        }
        th, td {
            border: 1px solid #dddddd;
            text-align: left;
            padding: 8px;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
    """

    # Start the table
    html = style + "<table>"
    html += "<tr><th>Date</th><th>Company</th><th>Title</th><th>Link</th></tr>"

    last_company = None
    for announcement in announcements:
        company = announcement['company']
        # Check for the absence of a link
        link = announcement['link'] if announcement['link'] else 'NA'
        link_text = f"<a href='{link}'>Go to Announcement</a>" if link != 'NA' else 'NIL'

        # Check if the current company is the same as the last one
        if company == last_company:
            # If so, continue the previous row (no need for a new company cell)
            html += f"<tr><td>{announcement['date']}</td><td></td><td>{announcement['title']}</td><td>{link_text}</td></tr>"
        else:
            # If not, end the previous row and start a new row with a new company cell
            html += f"<tr><td>{announcement['date']}</td><td>{company}</td><td>{announcement['title']}</td><td>{link_text}</td></tr>"
            last_company = company

    html += "</table>"
    return html

def generate_email_content(html_table):
    """Generate the full HTML content for the email, including introductory text."""
    previous_working_day = get_previous_working_day()
    introduction = """
    <p>Hi All!</p>
    <p>Here are the latest SGX announcements for """ + previous_working_day.strftime("%A, %Y-%m-%d") + """:</p>
    """
    # Combine introduction with the HTML table
    html_content = introduction + html_table
    return html_content



def send_email(recipients, html_content):
    """ Send an email with the announcements table """
    sender_email = ""  # Change to your sender email address
    sender_password = ""  # Change to your email password

    # Create MIME message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = ", ".join(recipients)
    message['Subject'] = 'Daily SGX Announcements'

    # Attach the HTML content
    message.attach(MIMEText(html_content, 'html'))

    # Setup the SMTP server and send the email
    server = smtplib.SMTP('smtp.office365.com', 587)
    server.starttls()  # Start TLS encryption
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipients, message.as_string())
    server.quit()

def emailANN(filepath):
    # Read announcements from saved csv file
    with open(filepath, 'r') as file:
        reader = csv.DictReader(file)
        announcements = [row for row in reader]

    html_table = create_html_table(announcements)
    html_content = generate_email_content(html_table)  # Generate full HTML content
    recipients = [""]  # Add recipients here
    send_email(recipients, html_content)


