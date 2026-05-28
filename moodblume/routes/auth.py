from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import re
from ..extensions import get_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not email or not password or not confirm_password:
            return render_template('auth/sign_up.html', error="All fields are required.")

        if password != confirm_password:
            return render_template('auth/sign_up.html', error="Passwords do not match. Please try again.")

        if len(password) < 8:
            return render_template('auth/sign_up.html', error="Password must be at least 8 characters.")
        if not re.search(r'[A-Z]', password):
            return render_template('auth/sign_up.html', error="Password must include at least one uppercase letter.")
        if not re.search(r'[0-9]', password):
            return render_template('auth/sign_up.html', error="Password must include at least one number.")
        if not re.search(r'[!@#$%^&*()_+\-=?]', password):
            return render_template('auth/sign_up.html', error="Password must include at least one symbol: ! @ # $ % ^ & * ( ) _ + - = ?")

        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        cursor = conn.cursor()
        try:

            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (email, email, hashed_password)
            )
            conn.commit()
            new_user_id = cursor.lastrowid
            cursor.close()
            conn.close()

            session['user_id'] = new_user_id
            session['username'] = email.split('@')[0].capitalize()
            return redirect(url_for('auth.welcome'))
        except mysql.connector.Error as e:
            cursor.close()
            conn.close()
            return render_template('auth/sign_up.html', error="Email address might already be registered. Try logging in!")
    return render_template('auth/sign_up.html')

@auth_bp.route('/welcome', methods=['GET', 'POST'])
def welcome():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        display_name = request.form.get('display_name', '').strip()
        if not display_name:
            return render_template('auth/welcome.html', error="Please enter how we should call you to continue.", hide_chrome=True)
        user_id = session['user_id']
        conn    = get_db_connection()
        cursor  = conn.cursor()
        cursor.execute(
            "UPDATE users SET username = %s, onboarded = 1 WHERE id = %s",
            (display_name, user_id)
        )
        session['username'] = display_name
        conn.commit()
        cursor.close()
        conn.close()
        session['onboarded'] = 1
        return redirect(url_for('main.sanctuary'))
    return render_template('auth/welcome.html', hide_chrome=True)

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            return render_template('auth/forgot_password.html', error="Please enter your email address.")

        return render_template(
            'auth/forgot_password.html',
            success="If an account is associated with this email, a reset link has been sent."
        )
    return render_template('auth/forgot_password.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password_attempt = request.form.get('password')
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and check_password_hash(user['password_hash'], password_attempt):
            session['user_id']   = user['id']
            session['onboarded'] = user.get('onboarded', 0)

            stored = user.get('username', '') or ''
            if stored and stored != email:
                session['username'] = stored
            else:
                session['username'] = email.split('@')[0].capitalize()

            if not user.get('onboarded'):
                return redirect(url_for('auth.welcome'))
            return redirect(url_for('main.sanctuary'))
        return render_template('auth/login.html', error="Invalid email or password. Please try again.")
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
