# from flask import Blueprint, request, render_template, redirect, session, flash, url_for
# from services.auth_service import register_user, authenticate_user
# # from services.user_service import fetch_user

# auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# @auth_bp.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         try:
#             register_user(request.form)
#             flash("Registration successful")
#             return redirect("/login")
#         except Exception as e:
#             flash(str(e))
#     return render_template("auth/register.html")

# @auth_bp.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         user = authenticate_user(
#             request.form.get("email"),
#             request.form.get("password")
#         )
#         if user:
#             session.clear()
#             session["user_id"] = user["Id"]
#             session["role"] = user["Role"]
#             user_id = session["user_id"]
#             # users = fetch_user(user_id)
#             return render_template("user/utilities/dashboard.html",)
#         flash("Invalid credentials")
#     return render_template("auth/login.html")

# from routes.decorators import login_required

# @auth_bp.route("/auth/dashboard")
# @login_required
# def dashboard():
#     return f"Dashboard — user id: {session.get('user_id')}"


# @auth_bp.route("/logout")
# def logout():
#     session.clear()
#     return redirect("/auth/login")

# from routes.decorators import role_required

# @auth_bp.route("/admin-test")
# @login_required
# @role_required("admin")
# def admin_test():
#     return "ADMIN ACCESS GRANTED"
