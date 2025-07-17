import os
import smtplib
from email.message import EmailMessage
import mysql.connector
from dotenv import load_dotenv

# Load .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")

TEST_MODE = True
TEST_RECIPIENT = GMAIL_USER  # sends only to yourself when testing

DISCOUNT_CODE = "ZABIHAH10"

# Read the HTML template
with open("existing_users_email.html", "r") as f:
    html_template = f.read()

# Compose the discount email
def compose_email(to_email, first_name):
    html_body = html_template.replace("ZABIHAH10", DISCOUNT_CODE)

    msg = EmailMessage()
    msg["Subject"] = "Exclusive Discount Just for You!"
    msg["From"] = GMAIL_USER
    msg["To"] = to_email

    msg.set_content(f"""
Hi {first_name or 'there'},

We appreciate you being part of the Zabihah community! 
Here’s an exclusive discount just for you — use code {DISCOUNT_CODE} at checkout for 10% off your next order.

Thank you for supporting us!

— The Zabihah Team
""")
    msg.add_alternative(html_body, subtype="html")

    return msg

# Connect to DB and fetch all users
conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
cursor = conn.cursor()
cursor.execute("""
    SELECT Email, FirstName 
    FROM user 
    WHERE IsDeleted = 0 AND Email IS NOT NULL AND Email != ''
""")

users = cursor.fetchall()
conn.close()

if not users:
    print("No users found.")
    exit()

print(f"📋 Found {len(users)} users. Sending emails...")

with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
    server.starttls()
    server.login(GMAIL_USER, GMAIL_PASS)

    for email, first_name in users:
        recipient = TEST_RECIPIENT if TEST_MODE else email
        msg = compose_email(recipient, first_name)

        try:
            server.send_message(msg)
            print(f"✅ Sent to: {recipient}")
        except Exception as e:
            print(f"❌ Failed to send to: {recipient} — {e}")

print("🎉 Done!")
