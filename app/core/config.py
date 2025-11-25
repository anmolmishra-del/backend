import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    # A sensible default for local development if user doesn't set POSTGRES URL.
     "postgresql+psycopg://postgres:admin@localhost:5432/data",
   # "postgresql+psycopg://odoo:odoo@localhost:5432/data",

)

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
