import psycopg

conn = psycopg.connect('postgresql://postgres:admin@localhost:5432/data')
cur = conn.cursor()
cur.execute('ALTER TABLE users ALTER COLUMN phone_number TYPE VARCHAR(32);')
conn.commit()
print('ALTER TABLE completed')
cur.close()
conn.close()
