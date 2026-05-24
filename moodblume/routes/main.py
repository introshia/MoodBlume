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
        return redirect(url_for('main.home'))
    return render_template('pages/index.html')


@main_bp.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    conn    = get_db_connection()
    cursor  = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM journal_entries WHERE user_id = %s ORDER BY entry_date DESC", (user_id,))
    all_entries = cursor.fetchall()
    cursor.execute("SELECT * FROM collections WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    user_collections = cursor.fetchall()
    conn.close()

    now               = datetime.now()
    current_month_str = now.strftime("%B %Y")
    shelves_data      = {}
    arts              = ['botanical', 'linen', 'face', 'wood', 'clouds']
    bgs               = ["#C8D898", "#EDE4D2", "#A8C4E4", "#DDBEAA", "#F0EAD6"]
    elastics          = ["#1a2810", "#222222", "#283858", "#604818", "#1A1A1A"]
    featured_journals = []

    for i, entry in enumerate(all_entries):
        display_text         = get_preview_text(entry['content'])
        entry['display_text']  = (display_text[:60] + '...') if len(display_text) > 60 else display_text
        entry['color_class']   = _COLOR_MAP.get(entry['mood_score'], _COLOR_MAP['default'])
        entry['formatted_date']= entry['entry_date'].strftime("%b %d")
        entry['mood_label']    = _MOOD_LABEL_MAP.get(entry['mood_score'], 'Steady')
        entry['month_label']   = entry['entry_date'].strftime("%B %Y")
        if not entry.get('collection_id'):
            month_year = entry['month_label']
            shelves_data.setdefault(month_year, []).append(entry)
        if i < 5:
            featured_journals.append({
                "id":              entry['id'],
                "title":           entry['formatted_date'],
                "pages":           entry['theme'] if (entry['theme'] and entry['theme'] != 'Default') else "Personal Chronicle",
                "elastic":         elastics[i % len(elastics)],
                "bg":              bgs[i % len(bgs)],
                "art":             arts[i % len(arts)],
                "content_preview": entry['display_text'],
            })

    all_entries_json = [{
        'id': e['id'], 'content': e['content'], 'display_text': e['display_text'],
        'color_class': e['color_class'], 'formatted_date': e['formatted_date'],
        'iso_date': e['entry_date'].strftime("%Y-%m-%d"), 'mood_score': e['mood_score'],
        'mood_label': e['mood_label'], 'month_label': e['month_label'],
        'collection_id': e.get('collection_id'),
    } for e in all_entries]

    user_collections_json = [{'id': c['id'], 'name': c['name'], 'cover_color': c['cover_color']} for c in user_collections]

    ordered_shelves = []
    if current_month_str in shelves_data:
        entries = shelves_data.pop(current_month_str)
        ordered_shelves.append({"label": "Currently Writing", "featured": entries[:3], "archive_count": max(0, len(entries) - 3)})
    else:
        ordered_shelves.append({"label": "Currently Writing", "featured": [], "archive_count": 0})
    for month in sorted(shelves_data, key=lambda x: datetime.strptime(x, "%B %Y"), reverse=True):
        entries = shelves_data[month]
        ordered_shelves.append({"label": month, "featured": entries[:3], "archive_count": max(0, len(entries) - 3)})

    for col in user_collections:
        col['entry_count'] = sum(1 for e in all_entries if e.get('collection_id') == col['id'])

    trend       = calculate_mood_trend(all_entries)
    chart_points = [{"label": e['entry_date'].strftime("%b %d"), "val": e['mood_score'],
                     "color": _CONFIG_MAP.get(e['mood_score'], _CONFIG_MAP[3])["c"],
                     "mood":  _MOOD_NAME_MAP.get(e['mood_score'], "neutral")} for e in reversed(all_entries[:15])]

    hour             = now.hour
    greeting_prefix  = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
    clean_username   = session.get('username', 'friend').replace('_', ' ').title()
    greeting         = f"{greeting_prefix}, {clean_username}."
    stats_msg        = f"You've inscribed {len(all_entries)} memories in your Archive this year."
    latest_text      = get_preview_text(all_entries[0]['content']) if all_entries else ""

    # Calculate current week's dates (Monday to Sunday) and map entries
    today = now.date()
    start_of_week = today - timedelta(days=today.weekday())
    week_days = []
    for i in range(7):
        day_date = start_of_week + timedelta(days=i)
        entry_on_day = None
        for e in all_entries:
            if e['entry_date'].date() == day_date:
                entry_on_day = e
                break
        
        if entry_on_day:
            week_days.append({
                "day_name": day_date.strftime("%a"),
                "day_num": day_date.day,
                "has_entry": True,
                "mood_score": entry_on_day['mood_score'],
                "mood_label": entry_on_day['mood_label'],
                "mood_color": _CONFIG_MAP.get(entry_on_day['mood_score'], _CONFIG_MAP[5])["c"],
                "color_class": entry_on_day['color_class'],
                "entry_id": entry_on_day['id']
            })
        else:
            week_days.append({
                "day_name": day_date.strftime("%a"),
                "day_num": day_date.day,
                "has_entry": False,
                "mood_score": None,
                "mood_label": "No Entry",
                "mood_color": "transparent",
                "color_class": "e-future" if day_date > today else "e-none",
                "entry_id": None
            })

    return render_template('pages/home.html',
        shelves=ordered_shelves, user_collections=user_collections,
        all_entries_json=all_entries_json, user_collections_json=user_collections_json,
        featured_journals=featured_journals, greeting=greeting, stats_msg=stats_msg,
        trend=trend, week_days=week_days,
        chart_labels=[p["label"] for p in chart_points],
        chart_scores=[p["val"]   for p in chart_points],
        chart_colors=[p["color"] for p in chart_points],
        chart_moods=[p["mood"]   for p in chart_points],
        companion=calculate_energy_data(latest_text),
        weekly=calculate_weekly_wrapup(all_entries),
        current_streak=calculate_streak(user_id))


@main_bp.route('/journal')
def journal():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    conn    = get_db_connection()
    cursor  = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM journal_entries WHERE user_id = %s ORDER BY entry_date DESC LIMIT 1", (user_id,))
    latest_entry = cursor.fetchone()
    conn.close()
    return render_template('pages/journal.html', latest_entry=latest_entry)


@main_bp.route('/your-collections')
def your_collections():
    return redirect(url_for('main.archive'))


@main_bp.route('/sanctuary')
def sanctuary():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    import json as _json
    user_id = session['user_id']
    streak  = calculate_streak(user_id)

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, content, entry_date FROM journal_entries WHERE user_id = %s ORDER BY entry_date DESC LIMIT 30",
        (user_id,)
    )
    recent_entries = cursor.fetchall()
    cursor.execute("""
        SELECT c.cover_color, c.art_style
        FROM journal_entries e
        LEFT JOIN collections c ON e.collection_id = c.id
        WHERE e.user_id = %s AND e.collection_id IS NOT NULL
        ORDER BY e.entry_date DESC LIMIT 1
    """, (user_id,))
    latest_journal = cursor.fetchone()
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

    return render_template('pages/sanctuary.html',
        streak_days=streak, recent_entries=processed_entries,
        active_bg=active_bg, active_art=active_art,
        open_journal=open_journal, target_entry_id=target_entry_id)


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

    return render_template('pages/your_collections.html',
        monthly_groups=monthly_groups,
        mood_groups=mood_groups,
        custom_collections=custom_collections,
        all_entries_json=all_entries_json,
        user_collections_json=user_collections_json)


@main_bp.route('/writing')
def writing():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('main.sanctuary', open='journal'))


@main_bp.route('/install')
def install():
    return render_template('pages/install.html')
