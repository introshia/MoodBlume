from datetime import date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.security import generate_password_hash
from ..extensions import get_db_connection

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    conn    = get_db_connection()
    cursor  = conn.cursor(dictionary=True)

    cursor.execute("SELECT username, joined_at FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) as total FROM journal_entries WHERE user_id = %s", (user_id,))
    total_entries = cursor.fetchone()['total']

    cursor.execute(
        "SELECT SUM(LENGTH(content) - LENGTH(REPLACE(content, ' ', '')) + 1) as words FROM journal_entries WHERE user_id = %s",
        (user_id,)
    )
    word_row    = cursor.fetchone()
    total_words = int(word_row['words']) if word_row and word_row['words'] else 0

    cursor.execute(
        "SELECT mood_score, COUNT(*) as cnt FROM journal_entries WHERE user_id = %s AND mood_score IS NOT NULL GROUP BY mood_score ORDER BY cnt DESC LIMIT 1",
        (user_id,)
    )
    mood_row   = cursor.fetchone()
    mood_labels = {1:'Angry',2:'Sad',3:'Anxious',4:'Confused',5:'Neutral',6:'Calm',7:'Hopeful',8:'Grateful',9:'Excited'}
    top_mood   = mood_labels.get(mood_row['mood_score'], 'Neutral') if mood_row else 'None yet'

    cursor.execute(
        "SELECT DISTINCT DATE(entry_date) as d FROM journal_entries WHERE user_id = %s ORDER BY d DESC",
        (user_id,)
    )
    days   = [row['d'] for row in cursor.fetchall()]
    streak = 0
    if days:
        check = date.today()
        for d in days:
            if d == check or d == check - timedelta(days=1):
                streak += 1
                check   = d
            else:
                break

    conn.close()
    joined = user['joined_at'].strftime("%B %Y") if user.get('joined_at') else "April 2026"
    return render_template('pages/profile.html',
        user=user, stats=total_entries, joined=joined,
        total_words=total_words, top_mood=top_mood, streak=streak)

@profile_bp.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id      = session['user_id']
    new_username = request.form.get('username')
    new_password = request.form.get('password')

    conn   = get_db_connection()
    cursor = conn.cursor()
    try:
        if new_username:
            cursor.execute("UPDATE users SET username = %s WHERE id = %s", (new_username, user_id))
            session['username'] = new_username
        if new_password:
            hashed = generate_password_hash(new_password)
            cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hashed, user_id))
        conn.commit()
        flash("Your curator identity has been successfully updated.")
    except Exception as e:
        flash(f"Error updating profile: {str(e)}")
    finally:
        conn.close()
    return redirect(url_for('profile.profile'))

@profile_bp.route('/sw.js')
def serve_sw():
    return current_app.send_static_file('sw.js')

def register_error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
