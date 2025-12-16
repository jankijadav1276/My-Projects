from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
import os

# ----- APP SETUP -----
app = Flask(__name__)

app.config['SECRET_KEY'] = 'nexgenhome_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'

# Initialize extensions
db = SQLAlchemy(app)
Session(app)

# ----- USER MODEL -----
class User(db.Model):
    __tablename__ = 'user'  # ensures consistent table name across versions
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        """Hashes and stores the user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies a user's password."""
        return check_password_hash(self.password_hash, password)


# ----- DATABASE CREATION -----
with app.app_context():
    db.create_all()


# ----- ROUTES -----

@app.route('/')
def index():
    """Redirect user to dashboard if logged in, else to login."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username_or_email or not password:
            flash("Please fill in all details.", "error")
            return render_template("login.html")

        # Try finding user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username/email or password.", "error")
            return render_template("login.html")

    return render_template("login.html")


# ---------- SIGNUP ----------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not username or not email or not password:
            flash("All fields are required.", "error")
            return render_template("signup.html")

        # Check duplicates
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "error")
            return render_template("signup.html")
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return render_template("signup.html")

        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Auto-login after signup
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        flash("Signup successful! Welcome to NexGenHome.", "success")
        return redirect(url_for('dashboard'))

    return render_template("signup.html")


# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))

    username = session.get('username')
    latest_user = User.query.order_by(User.id.desc()).first()

    return render_template("dashboard.html", user=username, latest_user=latest_user)


# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))


# ----- MAIN -----
if __name__ == '__main__':
    app.run(debug=True, port=5000)

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "users.db")

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///C:/Users/patel sakshi dilipbh/Downloads/mini project/New folder"