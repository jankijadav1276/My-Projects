from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

# ---------- APP SETUP ----------
app = Flask(__name__, instance_relative_config=True)
app.secret_key = "nexgenhome_secret_key"

# Ensure instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# ---------- DATABASE ----------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------- MODEL ----------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    @property
    def password(self):
        raise AttributeError("Password is write-only!")

    @password.setter
    def password(self, plain_password):
        self.password_hash = generate_password_hash(plain_password)

    def verify_password(self, plain_password):
        return check_password_hash(self.password_hash, plain_password)

# Create tables if not exist
with app.app_context():
    db.create_all()

# ---------- HOME ----------
@app.route('/')
def home():
    return render_template('index.html')

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_input = request.form['username']
        password = request.form['password']  # Correct input name

        user = User.query.filter(
            (User.username == user_input) | (User.email == user_input)
        ).first()

        if user and user.verify_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('room'))

        flash("Invalid login details")
    return render_template('login.html')

# ---------- SIGNUP ----------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if username or email exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return render_template('signup.html')

        if User.query.filter_by(email=email).first():
            flash("Email already exists")
            return render_template('signup.html')

        # Create user object
        user = User(username=username, email=email)
        user.password = password  # Hash and store

        # Add to DB
        db.session.add(user)
        db.session.commit()

        # Set session
        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('room'))

    return render_template('signup.html')

# ---------- ROOM ----------
@app.route('/room')
def room():
    if 'user_id' not in session:
        flash("Please login to access rooms.")
        return redirect(url_for('login'))
    return render_template('Room.html')

# ---------- ABOUT ----------
@app.route('/aboutUS')
def aboutUS():
    return render_template('aboutUS.html')

# ---------- CONTACT ----------
@app.route('/contactUS')
def contactUS():
    return render_template('contactUS.html')

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('home'))

# ---------- RUN ----------
if __name__ == '__main__':
    app.run(debug=True)