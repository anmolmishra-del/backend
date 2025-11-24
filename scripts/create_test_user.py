import sys
import os

# Allow importing app package
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.modules.auth.schemas import UserCreate
from app.modules.auth.services import create_user

u = UserCreate(username="testuser", password="TestPass123!", email="testuser@example.com", roles=["user"]) 

try:
    stored = create_user(u)
    print("Created user:", {"id": stored["id"], "username": stored["username"], "email": stored.get("email")})
except Exception as e:
    print("Failed to create user:", e)
    raise
