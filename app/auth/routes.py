from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User
from app.auth.forms import RegistrationForm, LoginForm

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        if User.query.filter_by(email=email).first():
            flash("Email address is already registered.", "danger")
            return render_template("register.html", form=form)

        status = "pending" if form.role.data == "examiner" else "active"

        user = User(
            name=form.name.data.strip(),
            email=email,
            password=generate_password_hash(form.password.data),
            role=form.role.data,
            department=form.department.data.strip() if form.department.data else None,
            phone=form.phone.data.strip() if form.phone.data else None,
            status=status
        )

        db.session.add(user)
        db.session.commit()

        if user.role == "examiner":
            flash("Registration successful. Wait for Admin approval.", "success")
        else:
            flash("Registration successful. You can now log in.", "success")

        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, form.password.data):
            if user.status == "pending":
                flash("Your examiner account is awaiting Admin approval.", "warning")
            elif user.status == "deactivated":
                flash("Your account has been deactivated.", "danger")
            elif user.status not in ["active", "approved"]:
                flash("Your account is not permitted to log in.", "danger")
            else:
                login_user(user)
                flash(f"Welcome, {user.name}!", "success")
                return redirect(url_for("main.index"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html", form=form)


@auth.route("/logout", methods=["POST"])
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("You have been logged out.", "info")

    return redirect(url_for("auth.login"))
