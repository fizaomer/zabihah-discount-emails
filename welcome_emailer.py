import smtplib
from email.message import EmailMessage
import mysql.connector
from dotenv import load_dotenv
import os

# Toggle test mode
TEST_MODE = True  # ✅ Set to False for production

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")

DISCOUNT_CODE = "WELCOME10"

# Connect to database
db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

cursor = db.cursor()

if TEST_MODE:
    print("🚧 Running in TEST_MODE: only emailing fizaomer23@gmail.com")
    cursor.execute("""
        SELECT Id, Email FROM user
        WHERE Email = 'fizaomer23@gmail.com'
    """)
else:
    print("✅ Running in PRODUCTION mode: emailing all new verified users from past 24 hours")
    cursor.execute("""
        SELECT Id, Email FROM user
        WHERE CreatedOn >= NOW() - INTERVAL 1 DAY
          AND IsEmailVerified = 1
    """)

users = cursor.fetchall()

if not users:
    print("ℹ️ No matching users found.")
    cursor.close()
    db.close()
    exit(0)

# Read the HTML template from file
with open("welcome_email.html", "r") as file:
    html_template = file.read()

for user_id, email in users:
    msg = EmailMessage()
    msg['Subject'] = "A special deal for you from Zabihah Shop!"
    msg['From'] = GMAIL_USER
    msg['To'] = email
    msg.set_content(f"""
Hi there,

Thank you for joining Zabihah!
We’re excited to have you on board.

As a welcome gift, here’s your exclusive discount code: {DISCOUNT_CODE}

Use it on your next order and enjoy!

— The Zabihah Team
""")

    # Attach HTML version as alternative
    msg.add_alternative(html_template, subtype='html')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(GMAIL_USER, GMAIL_PASS)
            smtp.send_message(msg)
        print(f"✅ Sent welcome email to {email}")
    except Exception as e:
        print(f"❌ Failed to send email to {email}: {e}")

cursor.close()
db.close()
