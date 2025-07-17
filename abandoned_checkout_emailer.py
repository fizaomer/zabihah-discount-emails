import os
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
import requests
import mysql.connector
from dotenv import load_dotenv

# Load env
load_dotenv()

SHOPIFY_PASSWORD = os.getenv("SHOPIFY_PASSWORD")
SHOPIFY_STORE = os.getenv("SHOPIFY_STORE")

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")

TEST_MODE = True
TEST_RECIPIENT = "fizaomer23@gmail.com"  # send to yourself in test mode
DISCOUNT_CODE = "ABANDON10"

# Time window: 30–60 min ago
now = datetime.utcnow()
start_time = (now - timedelta(minutes=7)).isoformat() + "Z"
end_time = (now - timedelta(minutes=2)).isoformat() + "Z"


print(f"📦 Fetching abandoned checkouts between {start_time} and {end_time}")

url = f"https://{SHOPIFY_STORE}/admin/api/2024-04/abandoned_checkouts.json"
headers = {
    "X-Shopify-Access-Token": SHOPIFY_PASSWORD
}
params = {
    "created_at_min": start_time,
    "created_at_max": end_time
}

resp = requests.get(url, headers=headers, params=params)
if resp.status_code != 200:
    print(f"❌ Failed to fetch checkouts: {resp.status_code} {resp.text}")
    exit(1)

checkouts = resp.json().get("checkouts", [])
if not checkouts:
    print("ℹ️ No abandoned checkouts in this window.")
    exit(0)

# Load HTML template
with open("abandoned_checkout_email.html", "r") as f:
    html_template = f.read()

# Connect DB
db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
cursor = db.cursor()

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(GMAIL_USER, GMAIL_PASS)

    for checkout in checkouts:
        email = checkout.get("email")
        checkout_url = checkout.get("abandoned_checkout_url")

        if not email or not checkout_url:
            continue

        # Skip already emailed
        cursor.execute("""
            SELECT COUNT(*) FROM email_logs
            WHERE user_email = %s AND email_type = 'abandoned_checkout'
        """, (email,))
        already_sent = cursor.fetchone()[0]
        if already_sent:
            print(f"✉️ Already emailed: {email}")
            continue

        recipient = TEST_RECIPIENT if TEST_MODE else email
        html_body = html_template.replace("{{CHECKOUT_URL}}", checkout_url)

        msg = EmailMessage()
        msg["Subject"] = "Complete your order and enjoy 10% off!"
        msg["From"] = GMAIL_USER
        msg["To"] = recipient
        msg.set_content("Looks like you left your cart. Click below to complete your order.")
        msg.add_alternative(html_body, subtype="html")

        try:
            smtp.send_message(msg)
            print(f"✅ Sent to: {recipient}")
            if not TEST_MODE:
                cursor.execute("""
                    INSERT INTO email_logs (user_email, email_type)
                    VALUES (%s, 'abandoned_checkout')
                """, (email,))
                db.commit()
        except Exception as e:
            print(f"❌ Failed to send to {recipient}: {e}")

cursor.close()
db.close()
print("🎉 Done.")
