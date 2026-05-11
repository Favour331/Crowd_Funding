from werkzeug.security import generate_password_hash, check_password_hash
from models.user import create_user, get_user_by_email

def register_user(data):
    hashed = generate_password_hash(data["password"])
    create_user(
        data["username"],
        data["first_name"],
        data["last_name"],
        data["email"],
        hashed,
        data.get("role", "backer")
    )

def authenticate_user(email, password):
    user = get_user_by_email(email)
    if not user:
        return None
    if not check_password_hash(user["Password"], password):
        return None
    return user
