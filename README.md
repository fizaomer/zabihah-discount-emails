# 📧 Zabihah Discounts Email Scripts

This repository contains Python scripts and HTML templates for sending automated discount and engagement emails to Zabihah users.

## Contents

- `.gitignore` — excludes sensitive files like `.env`
- `.env` — (excluded from repo) stores API keys and credentials
- `abandoned_checkout_email.html` — email template for abandoned carts
- `abandoned_checkout_emailer.py` — sends abandoned cart emails
- `existing_users_email.html` — template for existing user discounts
- `existing_users_emailer.py` — sends emails to existing users
- `thank_you_email.html` — thank-you email template
- `thank_you_emailer.py` — sends thank-you emails
- `welcome_email.html` — welcome email template
- `welcome_emailer.py` — sends welcome emails

## Requirements

- Python 3.7+
- Required packages:
  - `smtplib`
  - `email`
  - `dotenv`
  - `mysql-connector`
  - `requests`

Install dependencies:
```bash
pip install -r requirements.txt
```
## Environment Variables
Create a .env file in the root folder with the following keys:
```bash
SHOPIFY_PASSWORD=your-shopify-access-token
SHOPIFY_STORE=your-store.myshopify.com
DB_HOST=your-database-host
DB_USER=your-db-username
DB_PASSWORD=your-db-password
DB_NAME=your-db-name
GMAIL_USER=your-gmail-address
GMAIL_PASS=your-gmail-app-password
```
