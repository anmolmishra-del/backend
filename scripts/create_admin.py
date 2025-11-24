#!/usr/bin/env python
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, init_models
from app.modules.auth.models import User
from app.modules.auth.security import get_password_hash

def create_admin():
    init_models()
    session = SessionLocal()
    
    try:
        # Check if admin exists
        existing = session.query(User).filter(User.username == 'admin').first()
        if existing:
            print("✓ Admin user already exists")
            print(f"  Email: {existing.email}")
            print(f"  Username: {existing.username}")
            return
        
        # Create admin user
        hashed_pass = get_password_hash('admin123')
        admin = User(
            email='admin@example.com',
            username='admin',
            hashed_password=hashed_pass,
            first_name='Admin',
            last_name='User',
            role='admin',
            status='active',
            is_email_verified=True,
            roles=['admin']
        )
        session.add(admin)
        session.commit()
        
        print("✓ Admin user created!")
        print(f"  Email: admin@example.com")
        print(f"  Username: admin")
        print(f"  Password: admin123")
        print("\nUse these credentials to login to the admin panel at http://127.0.0.1:8001/admin")
        
    finally:
        session.close()

if __name__ == '__main__':
    create_admin()
