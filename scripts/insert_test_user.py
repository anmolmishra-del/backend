import psycopg
from datetime import datetime

conn = psycopg.connect('postgresql://postgres:admin@localhost:5432/data')
cur = conn.cursor()
cur.execute(
    """
    INSERT INTO users (email, username, hashed_password, first_name, last_name, phone_number, role, status, is_email_verified, roles, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id;
    """,
    (
        'testbig@example.com',
        'testbig',
        '$2b$12$aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'First',
        'Last',
        '123456788446',  # large phone number as string
        'user',
        'active',
        True,
        [],
        datetime.utcnow(),
        datetime.utcnow(),
    ),
)
new_id = cur.fetchone()[0]
conn.commit()
print('Inserted user id', new_id)
cur.close()
conn.close()
