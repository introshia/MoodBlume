import json
import io
from flask import Blueprint, request, session, send_file
from werkzeug.utils import secure_filename
from ..extensions import get_db_connection
from ..ai.helpers import analyze_sentiment, generate_letter, get_quote_for_entry

journal_bp = Blueprint('journal', __name__)

@journal_bp.route('/save_entry', methods=['POST'])
def save_entry():
    if 'user_id' not in session:
        return {'success': False, 'message': 'Unauthorized'}, 401

    try:
        data                 = request.get_json()
        content              = data.get('content', '').strip()
        mood_score_override  = data.get('mood_score', None)

        if not content:
            return {'success': False, 'message': 'Content cannot be empty'}, 400

        user_id   = session['user_id']
        ai_result = analyze_sentiment(content)
        mood_score = ai_result['score']
        quote      = get_quote_for_entry(content)
        collection_id = data.get('collection_id', None)

        entry_id = data.get('id', None)
        if not entry_id:
            try:
                content_data = json.loads(content)
                if isinstance(content_data, dict):
                    entry_id = content_data.get('id', None)
            except Exception:
                pass

        conn   = get_db_connection()
        cursor = conn.cursor()
        saved_id = None

        if entry_id:
            cursor.execute(
                "SELECT id FROM journal_entries WHERE id = %s AND user_id = %s",
                (entry_id, user_id)
            )
            if cursor.fetchone():
                cursor.execute(
                    "UPDATE journal_entries SET content = %s, mood_score = %s, collection_id = %s WHERE id = %s AND user_id = %s",
                    (content, mood_score, collection_id, entry_id, user_id)
                )
                conn.commit()
                saved_id = entry_id
            else:
                entry_id = None

        if not entry_id:
            cursor.execute(
                "INSERT INTO journal_entries (content, mood_score, theme, user_id, collection_id, entry_date) VALUES (%s, %s, %s, %s, %s, NOW())",
                (content, mood_score, 'Default', user_id, collection_id)
            )
            conn.commit()
            saved_id = cursor.lastrowid

        conn.close()

        username = session.get('username', 'friend')
        letter   = generate_letter(ai_result['score'], username, content)

        return {
            'success':     True,
            'message':     'Entry saved successfully',
            'id':          saved_id,
            'ai_analysis': ai_result,
            'quote':       quote.get('text') if quote else None,
            'letter':      letter,
        }, 200

    except Exception as e:
        return {'success': False, 'message': str(e)}, 500

@journal_bp.route('/upload_media', methods=['POST'])
def upload_media():
    if 'user_id' not in session:
        return {"error": "Unauthorized"}, 401
    if 'file' not in request.files:
        return {"error": "No file part"}, 400

    file = request.files['file']
    if file.filename == '':
        return {"error": "No selected file"}, 400

    filename  = secure_filename(file.filename)
    mimetype  = file.mimetype
    user_id   = session['user_id']
    file_data = file.read()

    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_media (user_id, filename, mimetype, media_data) VALUES (%s, %s, %s, %s)",
        (user_id, filename, mimetype, file_data)
    )
    media_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "url":  f"/get_media/{media_id}",
        "type": "video" if filename.lower().endswith(('.mp4', '.webm', '.mov')) else "image",
    }

@journal_bp.route('/get_media/<int:media_id>')
def get_media(media_id):
    if 'user_id' not in session:
        return "Unauthorized", 401

    user_id = session['user_id']
    conn    = get_db_connection()
    cursor  = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM user_media WHERE id = %s AND user_id = %s",
        (media_id, user_id)
    )
    media = cursor.fetchone()
    conn.close()

    if media:
        return send_file(
            io.BytesIO(media['media_data']),
            mimetype=media['mimetype'],
            download_name=media['filename']
        )
    return "Not Found", 404
