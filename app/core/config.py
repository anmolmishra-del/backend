import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    # A sensible default for local development if user doesn't set POSTGRES URL.
     "postgresql+psycopg://postgres:postgres@localhost:5432/hrms",
   # "postgresql+psycopg://odoo:odoo@localhost:5432/data",

)

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
auth_key = os.getenv("MSG91_AUTH_KEY")
otp_template_id = os.getenv("MSG91_OTP_TEMPLATE_ID")