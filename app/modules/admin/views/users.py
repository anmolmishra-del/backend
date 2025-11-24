



from sqladmin import ModelView

from app.modules.auth.models import User

from sqlalchemy import event

from app.modules.auth.security import get_password_hash

class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    column_list = [User.id, User.email, User.username, User.first_name, User.last_name, User.role, User.status, User.created_at]
    form_columns = [User.email, User.username, User.hashed_password, User.first_name, User.last_name, User.phone_number, User.role, User.status, User.is_email_verified]


    # Add event listener to hash password on insert/update
    @event.listens_for(User, "before_insert", propagate=True)
    @event.listens_for(User, "before_update", propagate=True)
    def receive_before_insert(mapper, connection, target):
        """Hash plain-text password before saving to DB."""
        pwd = target.hashed_password

        # Only hash if it's not already a bcrypt hash
        if pwd and not pwd.startswith("$2"):
            target.hashed_password = get_password_hash(pwd)