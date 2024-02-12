import sqlite3
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

# Import WTForms ValidationError
from wtforms.validators import ValidationError

# Generate secret key
secret_key = secrets.token_hex(24)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key

# Function to establish database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Define User model (assuming the database table is named 'users')
class User:
    def __init__(self, id=None, username=None, email=None, password_hash=None, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at

    @staticmethod
    def find_by_username(username):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        if user_data:
            return User(**user_data)
        return None

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Define registration form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.find_by_username(username.data)
        if user:
            raise ValidationError('Username is already taken. Please choose a different one.')

    def validate_email(self, email):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=?", (email.data,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        if user_data:
            raise ValidationError('Email is already registered. Please use a different one.')

# Define login form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Define application form
class ApplyForm(FlaskForm):
    university_id = StringField('University ID', validators=[DataRequired()])
    course_id = StringField('Course ID', validators=[DataRequired()])
    intake = StringField('Intake', validators=[DataRequired()])
    year = StringField('Year', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor()
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        cursor.execute("INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                       (user.username, user.email, user.password_hash, datetime.utcnow()))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Check if the user is an admin
        if form.username.data == 'admin' and form.password.data == 'admin_password':
            # If admin, redirect to admin page
            return redirect(url_for('admin'))
        else:
            # If not admin, proceed with regular user login
            user = User.find_by_username(form.username.data)
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password.', 'danger')
                return redirect(url_for('login'))
            # Login successful, render the main.html template
            return render_template('main.html', username=user.username)
    return render_template('login.html', form=form)

# Route for the universities page
@app.route('/universities')
def universities():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM universities")
    universities = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('uni.html', universities=universities)

# Route for the admin page
@app.route('/admin')
def admin():
    # Fetch the list of universities to populate the dropdown menu in the course form
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM universities")
    universities = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin.html', universities=universities)

# Route for showing courses of a specific university
@app.route('/courses/<int:university_id>')
def courses(university_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM courses WHERE university_id=?", (university_id,))
    courses = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('courses.html', courses=courses)

# Route for adding a new university
@app.route('/add_university', methods=['POST'])
def add_university():
    name = request.form['name']
    location = request.form['location']
    ranking = request.form['ranking']
    picture_url = request.form['picture_url']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO universities (name, location, ranking, picture_url) VALUES (?, ?, ?, ?)",
                   (name, location, ranking, picture_url))
    conn.commit()
    cursor.close()
    conn.close()

    flash('University added successfully.', 'success')
    return redirect(url_for('admin'))

# Route for adding a new course
@app.route('/add_course', methods=['POST'])
def add_course():
    university_id = request.form['university_id']
    course_name = request.form['course_name']
    duration_semesters = request.form['duration_semesters']
    description = request.form['description']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO courses (university_id, name, duration_semesters, description) VALUES (?, ?, ?, ?)",
                   (university_id, course_name, duration_semesters, description))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Course added successfully.', 'success')
    return redirect(url_for('admin'))

# Define application form
class ApplyForm(FlaskForm):
    university_id = StringField('University ID', validators=[DataRequired()])
    course_id = StringField('Course ID', validators=[DataRequired()])
    intake = StringField('Intake', validators=[DataRequired()])
    year = StringField('Year', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Route for the application page
@app.route('/apply', methods=['GET', 'POST'])
def apply():
    form = ApplyForm()
    if form.validate_on_submit():
        university_id = form.university_id.data
        course_id = form.course_id.data
        status = 'Pending'  # Assuming initial status is 'Pending'
        intake = form.intake.data
        year = form.year.data

        app.logger.info(f"Received application: university_id={university_id}, course_id={course_id}, intake={intake}, year={year}")

        # Insert the new application into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO applications (university_id, course_id, status, intake, year) VALUES (?, ?, ?, ?, ?)",
                       (university_id, course_id, status, intake, year))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Application added successfully.', 'success')
        return redirect(url_for('main'))  # Assuming 'main' is the route for main.html
    else:
        app.logger.error(f"Form validation failed: {form.errors}")

    return render_template('apply.html', form=form)

# Route for the main page
@app.route('/main')
def main():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(debug=True)
