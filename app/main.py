from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqlalchemy import event
from app.modules.auth import router as auth_router
from app.modules.admin import router as admin_router
from app.core.database import engine
from app.core.models import User
from app.core.security import get_password_hash


app = FastAPI(title="User Management API", version="1.0.0")


@app.get("/")
def root():
    return {"status": "ok", "message": "API is running"}


# # Add event listener to hash password on insert/update
# @event.listens_for(User, "before_insert", propagate=True)
# @event.listens_for(User, "before_update", propagate=True)
# def receive_before_insert(mapper, connection, target):
#     """Hash plain-text password before saving to DB."""
#     if target.hashed_password and not target.hashed_password.startswith('\\$'):
#         # If password doesn't start with bcrypt hash marker, hash it
#         target.hashed_password = get_password_hash(target.hashed_password)


# Setup SQLAdmin
admin = Admin(app=app, engine=engine, title="User Admin Panel", base_url="/admin")


# Create User ModelView for SQLAdmin - simple, no custom methods
class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    column_list = [User.id, User.email, User.username, User.first_name, User.last_name, User.role, User.status, User.created_at]
    form_columns = [User.email, User.username, User.hashed_password, User.first_name, User.last_name, User.phone_number, User.role, User.status, User.is_email_verified]


admin.add_view(UserAdmin)
app.include_router(auth_router)
app.include_router(admin_router)


@app.on_event("startup")
async def on_startup():
    try:
        from app.core.database import init_models
        init_models()
        print(" Database tables initialized")
    except Exception as e:
        print(f" Could not initialize database: {e}")
