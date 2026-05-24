from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from ..extensions import get_db_connection

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, hashed_password)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('auth.login'))
        except mysql.connector.Error:
            cursor.close()
            conn.close()
            return "Error: Username might already be taken. Try another!"
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username        = request.form['username']
        password_attempt = request.form['password']
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and check_password_hash(user['password_hash'], password_attempt):
            session['user_id']  = user['id']
            session['username'] = user['username']
            return redirect(url_for('main.sanctuary'))
        return "Invalid username or password. Please try again."
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
