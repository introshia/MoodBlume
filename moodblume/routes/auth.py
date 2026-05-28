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

        # Password strength validation
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
            # We set username to email to satisfy database constraints while keeping login strictly email-based
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (email, email, hashed_password)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('auth.login'))
        except mysql.connector.Error as e:
            cursor.close()
            conn.close()
            return render_template('auth/sign_up.html', error="Email address might already be registered. Try logging in!")
    return render_template('auth/sign_up.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            return render_template('auth/forgot_password.html', error="Please enter your email address.")
        
        # MOCK FLOW: Confirming receipt of the request
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
            session['user_id'] = user['id']
            # Save the clean local-part of email as username for sidebar/header display
            session['username'] = user['username'].split('@')[0].capitalize()
            return redirect(url_for('main.sanctuary'))
        return render_template('auth/login.html', error="Invalid email or password. Please try again.")
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
