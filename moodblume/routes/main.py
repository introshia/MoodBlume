from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, session
from ..extensions import get_db_connection
from ..ai.helpers import (
    calculate_mood_trend, calculate_energy_data, calculate_weekly_wrapup,
    calculate_streak, get_memory_entry, get_preview_text,
)

main_bp = Blueprint('main', __name__)

# ── Mood label maps ───────────────────────────────────────────────────────────
_MOOD_LABEL_MAP  = {1:'Angry',2:'Sad',3:'Anxious',4:'Confused',5:'Neutral',6:'Calm',7:'Hopeful',8:'Grateful',9:'Excited'}
_MOOD_NAME_MAP   = {9:"excited",8:"grateful",7:"hopeful",6:"calm",5:"neutral",4:"confused",3:"anxious",2:"sad",1:"angry"}
_COLOR_MAP       = {5:'c-sage',4:'c-slate',3:'c-ochre',2:'c-terr',1:'c-rose','default':'c-dust'}
_CONFIG_MAP      = {9:{"c":"#F2DD66"},8:{"c":"#FFB4D1"},7:{"c":"#85D0E8"},6:{"c":"#A8DADC"},5:{"c":"#DFDAC9"},4:{"c":"#C5C6D0"},3:{"c":"#B6AEE6"},2:{"c":"#A8C1ED"},1:{"c":"#FF9AA2"}}


@main_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main.sanctuary'))
    return render_template('pages/index.html')



@main_bp.route('/journal')
def journal():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    title = request.args.get('title') or request.args.get('collection') or request.args.get('collection_name') or ''
    conn    = get_db_connection()
    cursor  = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM journal_entries WHERE user_id = %s ORDER BY entry_date DESC LIMIT 1", (user_id,))
    latest_entry = cursor.fetchone()

    # Default the topbar title to the journal the user is currently writing in:
    # the collection of their latest entry, falling back to their newest journal.
    if not title:
        cursor.execute("""
            SELECT c.name
            FROM journal_entries e
            JOIN collections c ON e.collection_id = c.id
            WHERE e.user_id = %s AND e.collection_id IS NOT NULL
            ORDER BY e.entry_date DESC LIMIT 1
        """, (user_id,))
        row = cursor.fetchone()
        if not row:
            cursor.execute(
                "SELECT name FROM collections WHERE user_id = %s ORDER BY created_at DESC LIMIT 1",
                (user_id,)
            )
            row = cursor.fetchone()
        if row and row.get('name'):
            title = row['name']

    conn.close()
    return render_template('pages/journal.html', latest_entry=latest_entry, title=title)


@main_bp.route('/your-collections')
def your_collections():
    return redirect(url_for('main.archive'))


@main_bp.route('/sanctuary')
def sanctuary():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    import json as _json
    user_id = session['user_id']
    
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as count FROM collections WHERE user_id = %s", (user_id,))
    has_journals = cursor.fetchone()['count'] > 0
    
    if not has_journals:
        cursor.close()
        conn.close()
        return redirect(url_for('collections.new_journal'))

    streak  = calculate_streak(user_id)
    cursor.execute(
        "SELECT id, content, entry_date FROM journal_entries WHERE user_id = %s ORDER BY entry_date DESC LIMIT 30",
        (user_id,)
    )
    recent_entries = cursor.fetchall()
    cursor.execute("""
        SELECT c.cover_color, c.art_style
        FROM journal_entries e
        JOIN collections c ON e.collection_id = c.id
        WHERE e.user_id = %s AND e.collection_id IS NOT NULL
        ORDER BY e.entry_date DESC LIMIT 1
    """, (user_id,))
    latest_journal = cursor.fetchone()

    # Fall back to the user's most recently created journal — e.g. a brand-new
    # user who customized a journal but hasn't written any entries yet.
    if not latest_journal:
        cursor.execute("""
            SELECT cover_color, art_style
            FROM collections
            WHERE user_id = %s
            ORDER BY created_at DESC LIMIT 1
        """, (user_id,))
        latest_journal = cursor.fetchone()

    cursor.close()
    conn.close()

    active_bg  = latest_journal['cover_color'] or "#C8D898" if latest_journal else "#C8D898"
    active_art = latest_journal['art_style']   or "botanical" if latest_journal else "botanical"

    processed_entries = []
    for e in recent_entries:
        content_str = e['content'] or ""
        text = location = ""
        cats = []
        fav  = False
        if content_str.strip().startswith('{') and content_str.strip().endswith('}'):
            try:
                data     = _json.loads(content_str)
                text     = data.get('text', '').strip()
                location = data.get('location', '')
                cats     = data.get('cats', [])
                fav      = data.get('fav', False)
            except Exception:
                text = get_preview_text(content_str)
        else:
            text = get_preview_text(content_str)
        processed_entries.append({
            "id": e['id'], "text": text, "location": location,
            "cats": cats, "fav": fav,
            "formatted_date": e['entry_date'].strftime("%b %d") if e.get('entry_date') else "",
        })
    processed_entries.reverse()

    open_journal    = request.args.get('open_journal') == 'true'
    target_entry_id = request.args.get('entry_id', '')

    # Greeting + companion data (mirrors /home logic)
    now              = datetime.now()
    hour             = now.hour
    greeting_prefix  = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
    clean_username   = session.get('username', 'friend').replace('_', ' ').title()
    greeting         = f"{greeting_prefix}, {clean_username}."

    latest_text = ""
    if processed_entries:
        latest_text = processed_entries[-1].get('text', '')

    if streak <= 1:
        streak_stage = 'sprout'
    elif streak <= 4:
        streak_stage = 'stem'
    elif streak <= 6:
        streak_stage = 'bud'
    else:
        streak_stage = 'bloom'

    return render_template('pages/sanctuary.html',
        streak_days=streak, recent_entries=processed_entries,
        active_bg=active_bg, active_art=active_art,
        open_journal=open_journal, target_entry_id=target_entry_id,
        greeting=greeting, username=clean_username,
        companion=calculate_energy_data(latest_text),
        streak_stage=streak_stage, has_journals=True)


@main_bp.route('/archive')
def archive():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    conn    = get_db_connection()
    cursor  = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT DATE_FORMAT(entry_date, '%M') AS month_name, YEAR(entry_date) AS year,
               DATE_FORMAT(entry_date, '%Y-%m') AS month_key, COUNT(*) AS entry_count
        FROM journal_entries WHERE user_id = %s
        GROUP BY month_key, month_name, year ORDER BY month_key DESC
    """, (user_id,))
    monthly_groups = cursor.fetchall()
    cursor.execute("""
        SELECT mood_score, COUNT(*) AS entry_count
        FROM journal_entries
        WHERE user_id = %s AND mood_score IS NOT NULL
        GROUP BY mood_score
    """, (user_id,))
    mood_counts = {row['mood_score']: row['entry_count'] for row in cursor.fetchall()}
    mood_groups = []
    for score in (9, 8, 7, 6, 5, 4, 3, 2, 1):
        count = mood_counts.get(score)
        if not count:
            continue
        mood_groups.append({
            'mood_score': score,
            'mood_label': _MOOD_LABEL_MAP.get(score, 'Neutral'),
            'entry_count': count,
            'cover_color': _CONFIG_MAP.get(score, _CONFIG_MAP[5])['c'],
        })
    cursor.execute("SELECT * FROM collections WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    custom_collections = cursor.fetchall()
    cursor.execute("""
        SELECT collection_id, COUNT(*) AS entry_count
        FROM journal_entries
        WHERE user_id = %s AND collection_id IS NOT NULL
        GROUP BY collection_id
    """, (user_id,))
    volume_counts = {row['collection_id']: row['entry_count'] for row in cursor.fetchall()}
    for col in custom_collections:
        col['entry_count'] = volume_counts.get(col['id'], 0)

    cursor.execute("""
        SELECT id, content, entry_date, mood_score, collection_id,
               DATE_FORMAT(entry_date, '%%Y-%%m') AS month_key
        FROM journal_entries
        WHERE user_id = %s
        ORDER BY entry_date DESC
    """, (user_id,))
    entries_for_folders = cursor.fetchall()
    conn.close()

    for entry in entries_for_folders:
        preview = get_preview_text(entry.get('content') or '')
        entry['preview'] = (preview[:72] + '…') if len(preview) > 72 else preview
        entry['date_label'] = entry['entry_date'].strftime("%b %d") if entry.get('entry_date') else ''

    def _folder_previews(match_fn, limit=4):
        return [e for e in entries_for_folders if match_fn(e)][:limit]

    for mg in monthly_groups:
        key = mg['month_key']
        mg['previews'] = _folder_previews(lambda e, k=key: e.get('month_key') == k)
        mg['sticker_primary'] = '📅'
        mg['sticker_secondary'] = (mg['month_name'] or '')[:3].upper()

    _MOOD_STICKERS = {9: '☀️', 8: '💛', 7: '✨', 6: '🍃', 5: '○', 4: '🌀', 3: '🌧', 2: '💧', 1: '🔥'}
    for mg in mood_groups:
        score = mg['mood_score']
        mg['previews'] = _folder_previews(lambda e, s=score: e.get('mood_score') == s)
        mg['sticker_primary'] = _MOOD_STICKERS.get(score, '✿')
        mg['sticker_secondary'] = '✿'

    for col in custom_collections:
        cid = col['id']
        col['previews'] = _folder_previews(lambda e, c=cid: e.get('collection_id') == c)
        col['sticker_primary'] = '📖'
        col['sticker_secondary'] = (col.get('name') or 'V')[:1].upper()

    all_entries_json = [{
        'id': e['id'],
        'content': e['content'],
        'display_text': (get_preview_text(e['content'])[:60] + '...') if len(get_preview_text(e['content'])) > 60 else get_preview_text(e['content']),
        'color_class': _COLOR_MAP.get(e['mood_score'], _COLOR_MAP['default']),
        'formatted_date': e['entry_date'].strftime("%b %d"),
        'iso_date': e['entry_date'].strftime("%Y-%m-%d"),
        'mood_score': e['mood_score'],
        'mood_label': _MOOD_LABEL_MAP.get(e['mood_score'], 'Steady'),
        'month_label': e['entry_date'].strftime("%B %Y"),
        'collection_id': e.get('collection_id'),
    } for e in entries_for_folders]

    user_collections_json = [{'id': c['id'], 'name': c['name'], 'cover_color': c['cover_color']} for c in custom_collections]

    stats_msg = f"You've inscribed {len(entries_for_folders)} memories in your Archive this year."

    # Journal the user is currently writing in: the collection of their most
    # recent entry, falling back to their most recently created journal.
    active_journal = None
    for e in entries_for_folders:  # already ordered entry_date DESC
        if e.get('collection_id'):
            active_journal = next((c for c in custom_collections if c['id'] == e['collection_id']), None)
            if active_journal:
                break
    if not active_journal and custom_collections:
        active_journal = custom_collections[0]

    clean_username = session.get('username', 'friend').replace('_', ' ').title()

    # Mood-trend insight: a Linear Regression trend once there are a few entries,
    # or a single-entry read for the very first one.
    mood_insight = None
    if len(entries_for_folders) >= 2:
        # Pass the 10 most recent entries (in chronological order) to the model
        recent_for_model = list(reversed(entries_for_folders[:10]))
        trend_data = calculate_mood_trend(recent_for_model)

        # Map the model's 'status' to the UI text
        status = trend_data.get('status', 'Steady')
        if status == 'Bluming':
            mood_insight = "your mood has been brightening over your recent entries"
        elif status == 'Cloudy':
            mood_insight = "a few heavier days lately — be gentle with yourself"
        else:
            mood_insight = "your mood has held fairly steady lately"
    elif len(entries_for_folders) == 1:
        score = entries_for_folders[0].get('mood_score') or 5
        if score >= 7:
            mood_insight = "today's entry sounds bright and hopeful"
        elif score >= 5:
            mood_insight = "your mood seems okay today"
        elif score >= 3:
            mood_insight = "today carries a little weight — be gentle with yourself"
        else:
            mood_insight = "a heavier note today — be kind to yourself"

    return render_template('pages/your_collections.html',
        monthly_groups=monthly_groups,
        mood_groups=mood_groups,
        custom_collections=custom_collections,
        all_entries_json=all_entries_json,
        user_collections_json=user_collections_json,
        stats_msg=stats_msg,
        active_journal=active_journal,
        username=clean_username,
        mood_insight=mood_insight)


@main_bp.route('/writing')
def writing():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('main.sanctuary', open_journal='true'))


@main_bp.route('/install')
def install():
    return render_template('pages/install.html')
