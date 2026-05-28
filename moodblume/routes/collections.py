from flask import Blueprint, request, session
from ..extensions import get_db_connection

collections_bp = Blueprint('collections', __name__)


@collections_bp.route('/collections', methods=['GET'])
def list_collections():
    if 'user_id' not in session:
        return {'success': False, 'message': 'Unauthorized'}, 401
    user_id = session['user_id']
    conn    = get_db_connection()
    cursor  = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM collections WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    collections = cursor.fetchall()
    conn.close()
    for c in collections:
        if c.get('created_at'):
            c['created_at'] = c['created_at'].isoformat()
    return {'success': True, 'collections': collections}, 200


@collections_bp.route('/collections', methods=['POST'])
def create_collection():
    if 'user_id' not in session:
        return {'success': False, 'message': 'Unauthorized'}, 401
    try:
        data        = request.get_json()
        name        = data.get('name', '').strip()
        cover_color = data.get('cover_color', '#C8D898')
        art_style   = data.get('art_style', 'linen')
        paper_type  = data.get('paper_type', 'lined')
        page_type   = data.get('page_type', 'endless')
        if not name:
            return {'success': False, 'message': 'A collection needs a name.'}, 400
        user_id = session['user_id']
        conn    = get_db_connection()
        cursor  = conn.cursor()
        cursor.execute(
            "INSERT INTO collections (user_id, name, cover_color, art_style, paper_type, page_type) VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, name, cover_color, art_style, paper_type, page_type)
        )
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return {'success': True, 'id': new_id, 'name': name, 'cover_color': cover_color, 'art_style': art_style, 'paper_type': paper_type, 'page_type': page_type}, 201
    except Exception as e:
        return {'success': False, 'message': str(e)}, 500


@collections_bp.route('/new-journal', methods=['GET', 'POST'])
def new_journal():
    from flask import render_template, redirect, url_for, flash
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        name        = request.form.get('name', '').strip()
        cover_color = request.form.get('cover_color', '#C8D898')
        art_style   = request.form.get('art_style', 'linen')
        paper_type  = request.form.get('paper_type', 'lined')
        page_type   = request.form.get('page_type', 'endless')
        
        if not name:
            return render_template('auth/new_journal.html', error="Please enter a name for your journal.", hide_chrome=True)
            
        user_id = session['user_id']
        conn    = get_db_connection()
        cursor  = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO collections (user_id, name, cover_color, art_style, paper_type, page_type) VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, name, cover_color, art_style, paper_type, page_type)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('main.sanctuary'))
        except Exception as e:
            cursor.close()
            conn.close()
            return render_template('auth/new_journal.html', error=f"Error creating journal: {str(e)}", hide_chrome=True)
            
    return render_template('auth/new_journal.html', hide_chrome=True)


@collections_bp.route('/collections/<int:collection_id>', methods=['DELETE'])
def delete_collection(collection_id):
    if 'user_id' not in session:
        return {'success': False, 'message': 'Unauthorized'}, 401
    user_id = session['user_id']
    conn    = get_db_connection()
    cursor  = conn.cursor()
    cursor.execute("SELECT id FROM collections WHERE id = %s AND user_id = %s", (collection_id, user_id))
    if not cursor.fetchone():
        conn.close()
        return {'success': False, 'message': 'Not found or unauthorized'}, 404
    cursor.execute("UPDATE journal_entries SET collection_id = NULL WHERE collection_id = %s AND user_id = %s", (collection_id, user_id))
    cursor.execute("DELETE FROM collections WHERE id = %s", (collection_id,))
    conn.commit()
    conn.close()
    return {'success': True}, 200


@collections_bp.route('/collections/<int:collection_id>/assign', methods=['POST'])
def assign_entry_to_collection(collection_id):
    """Assign or re-assign an existing entry to a collection."""
    if 'user_id' not in session:
        return {'success': False, 'message': 'Unauthorized'}, 401
    try:
        data     = request.get_json()
        entry_id = data.get('entry_id')
        user_id  = session['user_id']
        conn     = get_db_connection()
        cursor   = conn.cursor()
        cursor.execute("SELECT id FROM journal_entries WHERE id = %s AND user_id = %s", (entry_id, user_id))
        if not cursor.fetchone():
            conn.close()
            return {'success': False, 'message': 'Entry not found'}, 404
        cursor.execute("UPDATE journal_entries SET collection_id = %s WHERE id = %s", (collection_id, entry_id))
        conn.commit()
        conn.close()
        return {'success': True}, 200
    except Exception as e:
        return {'success': False, 'message': str(e)}, 500
