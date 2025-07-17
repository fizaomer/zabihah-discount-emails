import requests
import mysql.connector
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load env vars
load_dotenv()

# 🔷 Toggle Test Mode
TEST_MODE = True  # ✅ set to False for production
TEST_EMAIL = "fizaomer23@gmail.com"

SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_PASSWORD = os.getenv("SHOPIFY_PASSWORD")
SHOPIFY_STORE = os.getenv("SHOPIFY_STORE")

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

GMAIL_USER = os.getenv("GMAIL_USER")  # set this to shop@zabihah.com in your .env
GMAIL_PASS = os.getenv("GMAIL_PASS")

DISCOUNT_CODE = "THANKYOU10"

# Read HTML email template
with open("thank_you_email.html", "r") as f:
    html_template = f.read()

# Time window: last 24 hours
since = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"

# Get delivered orders
print("📦 Fetching delivered orders…")
url = f"https://{SHOPIFY_STORE}/admin/api/2024-04/orders.json"
headers = {
    "X-Shopify-Access-Token": SHOPIFY_PASSWORD
}
params = {
    "status": "any",
    "fulfillment_status": "fulfilled",
    "created_at_min": since
}
resp = requests.get(url, headers=headers, params=params)

if resp.status_code != 200:
    print(f"❌ Failed to fetch orders: {resp.status_code} {resp.text}")
    exit(1)

orders = resp.json().get("orders", [])

if not orders:
    print("ℹ️ No delivered orders found in the last 24 hours.")
    exit(0)

# Connect to DB
db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
cursor = db.cursor()

for order in orders:
    customer = order.get("customer")
    if not customer:
        continue
    email = customer.get("email")
    if not email:
        continue

    # Check if already emailed
    cursor.execute("""
        SELECT COUNT(*) FROM email_logs
        WHERE user_email = %s AND email_type = 'thank_you'
    """, (email,))
    already_sent = cursor.fetchone()[0]

    if already_sent:
        print(f"✉️ Already sent thank-you email to {email}")
        continue

    # Prepare HTML body
    html_body = html_template.replace("THANKYOU10", DISCOUNT_CODE)

    # Compose email
    msg = EmailMessage()
    msg['Subject'] = "Thank You for Your Order — Enjoy 10% Off Next Time!"
    msg['From'] = GMAIL_USER
    msg['To'] = TEST_EMAIL if TEST_MODE else email

    msg.set_content("This is an HTML email. Please view it in an HTML-compatible email client.")
    msg.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(GMAIL_USER, GMAIL_PASS)
            smtp.send_message(msg)

        if TEST_MODE:
            print(f"✅ [TEST] Sent thank-you email to yourself at {TEST_EMAIL} (original customer: {email})")
        else:
            print(f"✅ Sent thank-you email to {email}")

            # Log it only if in production
            cursor.execute("""
                INSERT INTO email_logs (user_email, email_type)
                VALUES (%s, 'thank_you')
            """, (email,))
            db.commit()

    except Exception as e:
        print(f"❌ Failed to send email to {email}: {e}")

cursor.close()
db.close()
print("🎉 Done.")
