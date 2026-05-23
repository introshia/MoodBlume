import os
from dotenv import load_dotenv

# Load the hidden variables from your .env file
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, Response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import mysql.connector
import numpy as np
from datetime import datetime, timedelta
import io
from sklearn.linear_model import LinearRegression
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)
# Initialize VADER sentiment analyzer globally
analyzer = SentimentIntensityAnalyzer()
app.debug = True

# This keeps the user's login session secure!
app.secret_key = 'super_secret_moodblume_key'

# --- DATABASE CONFIGURATION ---
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': os.getenv('DB_PASSWORD'), 
    'database': 'moodblume_db'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.context_processor
def inject_sidebar_data():
    from flask import session as _session
    user_id = _session.get('user_id')
    if not user_id:
        return {}
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM collections WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        collections = cursor.fetchall()
        conn.close()
        return {'user_collections': collections}
    except Exception:
        return {'user_collections': []}

# --- AI & ANALYTICS LOGIC ---
def analyze_sentiment(content):
    """
    Uses the VADER (Valence Aware Dictionary and sEntiment Reasoner) library
    to analyze the entire entry for context, intensity, and negations.
    """
    if not content:
        return {"score": 3, "pillar": "peace", "reflection": "What is one truth you've been avoiding today?"}

    # Get sentiment scores from VADER
    vs = analyzer.polarity_scores(content)
    compound = vs['compound'] # Ranges from -1.0 to 1.0
    
    # Map compound score to 1-9 scale (to support the 12 nuanced faces)
    if compound >= 0.8: final_score = 9       # Excited / Happy
    elif compound >= 0.5: final_score = 8     # Grateful
    elif compound >= 0.2: final_score = 7     # Hopeful / Calm
    elif compound > -0.1: final_score = 5     # Neutral
    elif compound > -0.3: final_score = 4     # Confused
    elif compound > -0.5: final_score = 3     # Tired / Anxious
    elif compound > -0.8: final_score = 2     # Sad / Lonely
    else: final_score = 1                     # Angry

    # Pillar Detection (keywords are still good for categorizing 'topics')
    text = content.lower()
    pillar = "Peace"
    if any(w in text for w in ['work', 'time', 'manage', 'schedule', 'todo', 'busy', 'deadline']): pillar = "Balance"
    elif any(w in text for w in ['learn', 'new', 'goal', 'better', 'future', 'skill', 'try', 'growth']): pillar = "Growth"
    elif any(w in text for w in ['health', 'body', 'eat', 'sleep', 'energy', 'feeling', 'wellness']): pillar = "Wellness"
    elif any(w in text for w in ['quiet', 'still', 'calm', 'nature', 'breathe', 'meditate', 'peace']): pillar = "Peace"

    # Dynamic Reflection Logic
    questions = {
        "Balance": "Is it the quantity of tasks—or the weight of expectations—that truly feels out of balance today?",
        "Growth": "What part of this 'new' self are you most afraid to leave behind as you grow?",
        "Wellness": "If your body could speak without using words right now, what's the first thing it would ask for?",
        "Peace": "In the middle of this quiet moment, what's the one noise you're still trying to ignore?"
    }
    
    reflection = questions.get(pillar, "What is one truth you've been avoiding today?")
    if final_score >= 4: reflection = "This vibrancy feels real—how can you preserve a piece of this light for a darker day?"
    elif final_score <= 2: reflection = "When the weight feels this heavy, what is the smallest possible kindness you can show yourself?"

    return {
        "score": final_score,
        "compound": compound,
        "pillar": pillar.lower(),
        "reflection": reflection
    }

def get_quote_for_entry(content):
    content = content.lower()
    category = 'happy'
    if any(word in content for word in ['sad', 'down', 'cry']): category = 'sad'
    elif any(word in content for word in ['stress', 'hard', 'exam']): category = 'stressed'
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM quotes WHERE category = %s ORDER BY RAND() LIMIT 1", (category,))
    quote = cursor.fetchone()
    conn.close()
    return quote

def calculate_mood_trend(entries):
    if len(entries) < 2: 
        return {"status": "Seeding", "slope": 0, "msg": "The pages are fresh.", "consistency": "Write your first entry."}
    
    # Linear Regression Logic - Using Valence (Compound Score) for technical accuracy
    # If content is available, we use the raw sentiment decimal (-1.0 to 1.0)
    # This fulfills the scientific requirement for linear regression on continuous data.
    X = np.array(range(len(entries))).reshape(-1, 1)
    
    y = []
    for e in reversed(entries):
        # Fallback to mood_score mapped to -1 to 1 if content is missing
        val = e.get('mood_score', 5) / 4.5 - 1.0 
        if e.get('content'):
            try:
                # Re-calculate or use stored compound if we had it
                text = e['content']
                if isinstance(text, str) and (text.startswith('{') or text.startswith('[')):
                    import json
                    text = json.loads(text).get('text', text)
                val = analyzer.polarity_scores(text)['compound']
            except: pass
        y.append(val)
        
    y = np.array(y)
    model = LinearRegression().fit(X, y)
    slope = model.coef_[0]
    
    # Map technical slope to Whimsical Status
    status = "Bluming" if slope > 0.05 else "Cloudy" if slope < -0.05 else "Steady"
    return {
        "status": status, 
        "slope": round(slope, 4), 
        "msg": f"Your emotional rhythm is {status}.", 
        "consistency": "Consistent."
    }

def calculate_advanced_insights(entries):
    if len(entries) < 3:
        return None
    
    # 1. THE THERAPY MODEL (Word Count vs Mood)
    # X = Word Count, Y = Compound Score
    X_words = []
    y_scores = []
    
    # 2. THE RHYTHM MODEL (Time of Day vs Mood)
    # X = Hour, Y = Compound Score
    X_time = []
    
    for e in entries:
        content = e.get('content', '')
        # Handle JSON content
        if content.startswith('{'):
            import json
            try: content = json.loads(content).get('text', '')
            except: pass
        
        word_count = len(content.split())
        hour = e['entry_date'].hour + (e['entry_date'].minute / 60)
        
        # We use mood_score normalized to 0-1 for regression targets
        score = (e.get('mood_score', 5) - 1) / 8.0 
        
        X_words.append([word_count])
        X_time.append([hour])
        y_scores.append(score)
        
    y_scores = np.array(y_scores)
    
    # Fit Word Model
    word_model = LinearRegression().fit(np.array(X_words), y_scores)
    word_slope = word_model.coef_[0]
    
    # Fit Time Model
    time_model = LinearRegression().fit(np.array(X_time), y_scores)
    time_slope = time_model.coef_[0]
    
    # Predict tomorrow's mood based on time trend (Velocity)
    # Just a simple projection of the recent trend
    X_trend = np.array(range(len(entries))).reshape(-1, 1)
    trend_model = LinearRegression().fit(X_trend, y_scores)
    prediction = trend_model.predict([[len(entries) + 1]])[0]
    
    # Human-readable interpretations
    word_insight = "Longer entries correlate with better clarity." if word_slope > 0.001 else "Your mood stays stable regardless of length."
    time_insight = "Your energy peaks in the evening." if time_slope > 0.01 else "Morning reflections bring you more peace." if time_slope < -0.01 else "Your mood is consistent throughout the day."
    
    return {
        "word_slope": round(word_slope * 100, 2),
        "word_msg": word_insight,
        "time_msg": time_insight,
        "predicted_energy": round(prediction * 100, 1),
        "predicted_label": "High" if prediction > 0.7 else "Moderate" if prediction > 0.4 else "Restorative"
    }
def calculate_energy_data(content):
    if not content:
        return {"score": 50, "mood": "neutral", "label": "Resting", "color": "#F5C842"}
    
    c = content.lower()
    # Basic Energy Analysis (Keywords + Length)
    high = ['excited', 'amazing', 'great', 'love', 'happy', 'bloom', 'wonderful', 'active']
    low = ['tired', 'exhausted', 'sad', 'bad', 'lonely', 'drain', 'heavy', 'storm']
    
    score = 50
    if any(word in c for word in high): score += 30
    if any(word in c for word in low): score -= 30
    
    # Emotional Nuance
    if len(c) > 200: score += 10 # Long reflections = higher energy
    score = max(0, min(100, score))
    
    if score >= 80:
        return {"score": score, "mood": "high", "label": "Happy", "color": "#5BB8F5", "light": "#98D3F5", "dark": "#2A88BF", "mouth": "M3 3 Q11 12 19 3"}
    elif score >= 60:
        return {"score": score, "mood": "balanced", "label": "Calm", "color": "#6DBF8A", "light": "#9DDBB0", "dark": "#3A8A56", "mouth": "M3 6 Q11 2 19 6"}
    elif score >= 40:
        return {"score": score, "mood": "neutral", "label": "Neutral", "color": "#F5C842", "light": "#FAE092", "dark": "#BF9210", "mouth": "M4 5 L18 5"}
    elif score >= 20:
        return {"score": score, "mood": "low", "label": "Sad", "color": "#E87FA0", "light": "#FFAAC4", "dark": "#B54A6E", "mouth": "M3 3 Q11 9 19 3"}
    else:
        return {"score": score, "mood": "drained", "label": "Stressed", "color": "#A99BC4", "light": "#C4B5E8", "dark": "#7E6BA9", "mouth": "M5 3 Q11 3 17 3"}

def calculate_streak(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT DISTINCT DATE(entry_date) as entry_date 
        FROM journal_entries 
        WHERE user_id = %s 
        ORDER BY entry_date DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return 0
        
    today = datetime.now().date()
    last_entry_date = rows[0]['entry_date']
    
    if last_entry_date < (today - timedelta(days=1)):
        return 0
    
    streak = 1
    current_date = last_entry_date
    for row in rows[1:]:
        if row['entry_date'] == (current_date - timedelta(days=1)):
            streak += 1
            current_date = row['entry_date']
        else:
            break
            
    return streak

def calculate_weekly_wrapup(entries):
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    
    recent_entries = [e for e in entries if e['entry_date'] >= week_ago]
    
    active_days = len(set(e['entry_date'].date() for e in recent_entries))
    total_entries = len(recent_entries)
    
    # Estimate writing time: ~40 words per minute average journaling speed
    total_words = 0
    for e in recent_entries:
        content = e.get('content', '')
        if content.startswith('{'):
            import json
            try: content = json.loads(content).get('text', '')
            except: pass
        total_words += len(content.split())
        
    total_minutes = total_words // 40
    seconds = int(((total_words / 40) - total_minutes) * 60)
    
    start_date_str = week_ago.strftime("%d %b")
    end_date_str = now.strftime("%d %b")
    
    # We use some faux comparison arrows for the UI (e.g. up/down)
    # Since we don't have last week's data easily separated here, we'll randomize or use a simple heuristic for the arrows
    # In a real app, you'd compare with the previous 7 days.
    
    return {
        "date_range": f"{start_date_str} - {end_date_str}",
        "days": active_days,
        "entries": total_entries,
        "minutes": total_minutes,
        "seconds": seconds,
        "days_dir": "up" if active_days >= 3 else "down",
        "entries_dir": "up" if total_entries >= 3 else "down",
        "time_dir": "down" if total_minutes < 5 else "up"
    }

def get_preview_text(content):
    if not content: return ""
    
    # Check if content is JSON (typical for Sanctuary canvas saves)
    if content.strip().startswith('{') and content.strip().endswith('}'):
        import json
        try:
            data = json.loads(content)
            if 'text' in data:
                return data['text'].strip().replace('\n', ' ')
        except:
            pass
            
    return content.strip().replace('\n', ' ')



# --- AUTHENTICATION ROUTES ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            cursor.close()
            conn.close()
            return f"Error: Username might already be taken. Try another!"

    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_attempt = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password_attempt):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('sanctuary')) 
        else:
            return "Invalid username or password. Please try again."

    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('login'))


# --- MAIN APP ROUTES ---

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template('pages/index.html')


@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM journal_entries WHERE user_id = %s ORDER BY entry_date DESC", (user_id,))
    all_entries = cursor.fetchall()
    cursor.execute("SELECT * FROM collections WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    user_collections = cursor.fetchall()
    conn.close()

    now = datetime.now()
    current_month_str = now.strftime("%B %Y")
    shelves_data = {}
    color_map = {5: 'c-sage', 4: 'c-slate', 3: 'c-ochre', 2: 'c-terr', 1: 'c-rose', 'default': 'c-dust'}
    arts = ['botanical', 'linen', 'face', 'wood', 'clouds']
    bgs = ["#C8D898", "#EDE4D2", "#A8C4E4", "#DDBEAA", "#F0EAD6"]
    elastics = ["#1a2810", "#222222", "#283858", "#604818", "#1A1A1A"]
    featured_journals = []
    mood_label_map = {1: 'Angry', 2: 'Sad', 3: 'Anxious', 4: 'Confused', 5: 'Neutral', 6: 'Calm', 7: 'Hopeful', 8: 'Grateful', 9: 'Excited'}

    for i, entry in enumerate(all_entries):
        display_text = get_preview_text(entry['content'])
        entry['display_text'] = (display_text[:60] + '...') if len(display_text) > 60 else display_text
        entry['color_class'] = color_map.get(entry['mood_score'], color_map['default'])
        entry['formatted_date'] = entry['entry_date'].strftime("%b %d")
        entry['mood_label'] = mood_label_map.get(entry['mood_score'], 'Steady')
        entry['month_label'] = entry['entry_date'].strftime("%B %Y")
        if not entry.get('collection_id'):
            month_year = entry['month_label']
            if month_year not in shelves_data:
                shelves_data[month_year] = []
            shelves_data[month_year].append(entry)
        if i < 5:
            featured_journals.append({
                "id": entry['id'],
                "title": entry['formatted_date'],
                "pages": entry['theme'] if (entry['theme'] and entry['theme'] != 'Default') else "Personal Chronicle",
                "elastic": elastics[i % len(elastics)],
                "bg": bgs[i % len(bgs)],
                "art": arts[i % len(arts)],
                "content_preview": entry['display_text']
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
        entries = shelves_data[current_month_str]
        ordered_shelves.append({"label": "Currently Writing", "featured": entries[:3], "archive_count": max(0, len(entries) - 3)})
        del shelves_data[current_month_str]
    else:
        ordered_shelves.append({"label": "Currently Writing", "featured": [], "archive_count": 0})
    for month in sorted(shelves_data.keys(), key=lambda x: datetime.strptime(x, "%B %Y"), reverse=True):
        entries = shelves_data[month]
        ordered_shelves.append({"label": month, "featured": entries[:3], "archive_count": max(0, len(entries) - 3)})

    for col in user_collections:
        col['entry_count'] = sum(1 for e in all_entries if e.get('collection_id') == col['id'])

    trend = calculate_mood_trend(all_entries)
    config_map = {9: {"c": "#F2DD66"}, 8: {"c": "#FFB4D1"}, 7: {"c": "#85D0E8"}, 6: {"c": "#A8DADC"}, 5: {"c": "#DFDAC9"}, 4: {"c": "#C5C6D0"}, 3: {"c": "#B6AEE6"}, 2: {"c": "#A8C1ED"}, 1: {"c": "#FF9AA2"}}
    mood_name_map = {9: "excited", 8: "grateful", 7: "hopeful", 6: "calm", 5: "neutral", 4: "confused", 3: "anxious", 2: "sad", 1: "angry"}
    chart_points = [{"label": e['entry_date'].strftime("%b %d"), "val": e['mood_score'], "color": config_map.get(e['mood_score'], config_map[3])["c"], "mood": mood_name_map.get(e['mood_score'], "neutral")} for e in reversed(all_entries[:15])]

    hour = now.hour
    greeting_prefix = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
    clean_username = session.get('username', 'friend').replace('_', ' ').title()
    greeting = f"{greeting_prefix}, {clean_username}."
    stats_msg = f"You've inscribed {len(all_entries)} memories in your Archive this year."
    latest_text = get_preview_text(all_entries[0]['content']) if all_entries else ""

    return render_template('pages/archive.html',
                           shelves=ordered_shelves, user_collections=user_collections,
                           all_entries_json=all_entries_json, user_collections_json=user_collections_json,
                           featured_journals=featured_journals, greeting=greeting, stats_msg=stats_msg,
                           trend=trend, insights=calculate_advanced_insights(all_entries),
                           chart_labels=[p["label"] for p in chart_points],
                           chart_scores=[p["val"] for p in chart_points],
                           chart_colors=[p["color"] for p in chart_points],
                           chart_moods=[p["mood"] for p in chart_points],
                           companion=calculate_energy_data(latest_text),
                           weekly=calculate_weekly_wrapup(all_entries),
                           current_streak=calculate_streak(user_id))


@app.route('/journal')
def journal():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM journal_entries WHERE user_id = %s ORDER BY entry_date DESC LIMIT 1", (user_id,))
    latest_entry = cursor.fetchone()
    conn.close()
    return render_template('pages/journal.html', latest_entry=latest_entry)


@app.route('/your-collections')
def your_collections():
    return redirect(url_for('archive'))


@app.route('/sanctuary')
def sanctuary():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    streak = calculate_streak(user_id)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, content, entry_date FROM journal_entries WHERE user_id = %s ORDER BY entry_date DESC LIMIT 30", (user_id,))
    recent_entries = cursor.fetchall()
    
    # Determine the "current journal" style based on the latest entry's collection
    cursor.execute("""
        SELECT c.cover_color, c.art_style 
        FROM journal_entries e 
        LEFT JOIN collections c ON e.collection_id = c.id 
        WHERE e.user_id = %s AND e.collection_id IS NOT NULL
        ORDER BY e.entry_date DESC LIMIT 1
    """, (user_id,))
    latest_journal = cursor.fetchone()
    
    active_bg = "#C8D898"
    active_art = "botanical"
    if latest_journal:
        active_bg = latest_journal['cover_color'] or active_bg
        active_art = latest_journal['art_style'] or active_art
        
    conn.close()
    
    processed_entries = []
    for e in recent_entries:
        content_str = e['content'] or ""
        text = ""
        location = ""
        cats = []
        fav = False
        
        if content_str.strip().startswith('{') and content_str.strip().endswith('}'):
            import json
            try:
                data = json.loads(content_str)
                text = data.get('text', '').strip()
                location = data.get('location', '')
                cats = data.get('cats', [])
                fav = data.get('fav', False)
            except Exception:
                text = get_preview_text(content_str)
        else:
            text = get_preview_text(content_str)
            
        formatted_date = e['entry_date'].strftime("%b %d") if e.get('entry_date') else ""
        processed_entries.append({
            "id": e['id'], 
            "text": text, 
            "location": location, 
            "cats": cats, 
            "fav": fav, 
            "formatted_date": formatted_date
        })
        
    processed_entries.reverse()
    
    open_journal = request.args.get('open_journal') == 'true'
    target_entry_id = request.args.get('entry_id', '')
    
    return render_template('pages/sanctuary.html', streak_days=streak, recent_entries=processed_entries, active_bg=active_bg, active_art=active_art, open_journal=open_journal, target_entry_id=target_entry_id)

@app.route('/archive')
def archive():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT DATE_FORMAT(entry_date, '%M') AS month_name, YEAR(entry_date) AS year,
               DATE_FORMAT(entry_date, '%Y-%m') AS month_key, COUNT(*) AS entry_count
        FROM journal_entries WHERE user_id = %s
        GROUP BY month_key, month_name, year ORDER BY month_key DESC
    """, (user_id,))
    monthly_groups = cursor.fetchall()
    cursor.execute("SELECT * FROM collections WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    custom_collections = cursor.fetchall()
    conn.close()
    return render_template('pages/your_collections.html',
                           monthly_groups=monthly_groups,
                           custom_collections=custom_collections)



# ── COLLECTION API ROUTES ──────────────────────────────────────────────────────

@app.route('/collections', methods=['GET'])
def list_collections():
    if 'user_id' not in session:
        return {'success': False, 'message': 'Unauthorized'}, 401
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM collections WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    collections = cursor.fetchall()
    conn.close()
    # Convert datetimes to strings for JSON
    for c in collections:
        if c.get('created_at'):
            c['created_at'] = c['created_at'].isoformat()
    return {'success': True, 'collections': collections}, 200


@app.route('/collections', methods=['POST'])
def create_collection():
    if 'user_id' not in session:
        return {'success': False, 'message': 'Unauthorized'}, 401
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        cover_color = data.get('cover_color', '#C8D898')
        art_style = data.get('art_style', 'linen')
        if not name:
            return {'success': False, 'message': 'A collection needs a name.'}, 400
        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO collections (user_id, name, cover_color, art_style) VALUES (%s, %s, %s, %s)",
            (user_id, name, cover_color, art_style)
        )
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return {'success': True, 'id': new_id, 'name': name, 'cover_color': cover_color, 'art_style': art_style}, 201
    except Exception as e:
        return {'success': False, 'message': str(e)}, 500


@app.route('/collections/<int:collection_id>', methods=['DELETE'])
def delete_collection(collection_id):
    if 'user_id' not in session:
        return {'success': False, 'message': 'Unauthorized'}, 401
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    # Verify ownership before deleting
    cursor.execute("SELECT id FROM collections WHERE id = %s AND user_id = %s", (collection_id, user_id))
    if not cursor.fetchone():
        conn.close()
        return {'success': False, 'message': 'Not found or unauthorized'}, 404
    # Un-assign entries (ON DELETE SET NULL handles this, but be explicit)
    cursor.execute("UPDATE journal_entries SET collection_id = NULL WHERE collection_id = %s", (collection_id,))
    cursor.execute("DELETE FROM collections WHERE id = %s", (collection_id,))
    conn.commit()
    conn.close()
    return {'success': True}, 200


@app.route('/collections/<int:collection_id>/assign', methods=['POST'])
def assign_entry_to_collection(collection_id):
    """Assign or re-assign an existing entry to a collection."""
    if 'user_id' not in session:
        return {'success': False, 'message': 'Unauthorized'}, 401
    try:
        data = request.get_json()
        entry_id = data.get('entry_id')
        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor()
        # Verify entry ownership
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

@app.route('/writing')
def writing():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('sanctuary', open='journal'))



@app.route('/install')
def install():
    return render_template('pages/install.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT username, joined_at FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) as total FROM journal_entries WHERE user_id = %s", (user_id,))
    total_entries = cursor.fetchone()['total']

    cursor.execute("SELECT SUM(LENGTH(content) - LENGTH(REPLACE(content, ' ', '')) + 1) as words FROM journal_entries WHERE user_id = %s", (user_id,))
    word_row = cursor.fetchone()
    total_words = int(word_row['words']) if word_row and word_row['words'] else 0

    # Top mood: map mood_score int to a label
    cursor.execute("SELECT mood_score, COUNT(*) as cnt FROM journal_entries WHERE user_id = %s AND mood_score IS NOT NULL GROUP BY mood_score ORDER BY cnt DESC LIMIT 1", (user_id,))
    mood_row = cursor.fetchone()
    mood_labels = {1: 'Angry', 2: 'Sad', 3: 'Anxious', 4: 'Confused', 5: 'Neutral', 6: 'Calm', 7: 'Hopeful', 8: 'Grateful', 9: 'Excited'}
    top_mood = mood_labels.get(mood_row['mood_score'], 'Neutral') if mood_row else 'None yet'

    cursor.execute("SELECT DISTINCT DATE(entry_date) as d FROM journal_entries WHERE user_id = %s ORDER BY d DESC", (user_id,))
    days = [row['d'] for row in cursor.fetchall()]
    streak = 0
    if days:
        from datetime import date, timedelta
        check = date.today()
        for d in days:
            if d == check or d == check - timedelta(days=1):
                streak += 1
                check = d
            else:
                break

    conn.close()
    joined = user['joined_at'].strftime("%B %Y") if user.get('joined_at') else "April 2026"
    return render_template('pages/profile.html', user=user, stats=total_entries, joined=joined, total_words=total_words, top_mood=top_mood, streak=streak)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    new_username = request.form.get('username')
    new_password = request.form.get('password')
    
    conn = get_db_connection()
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
        
    return redirect(url_for('profile'))

@app.route('/save_entry', methods=['POST'])
def save_entry():
    # SECURITY
    if 'user_id' not in session:
        return {'success': False, 'message': 'Unauthorized'}, 401
    
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        mood_score_override = data.get('mood_score', None)
        
        if not content:
            return {'success': False, 'message': 'Content cannot be empty'}, 400
        
        user_id = session['user_id']
        
        # Analyze sentiment from content
        ai_result = analyze_sentiment(content)
        mood_score = ai_result['score']
        
        # Get a relevant quote (legacy support)
        quote = get_quote_for_entry(content)
        
        # Optional: assign to a collection on save
        collection_id = data.get('collection_id', None)

        # Check for id to see if it's an update
        entry_id = data.get('id', None)
        if not entry_id:
            try:
                import json
                content_data = json.loads(content)
                if isinstance(content_data, dict):
                    entry_id = content_data.get('id', None)
            except Exception:
                pass

        conn = get_db_connection()
        cursor = conn.cursor()
        
        saved_id = None
        if entry_id:
            # Check if this entry exists and belongs to the user
            cursor.execute("SELECT id FROM journal_entries WHERE id = %s AND user_id = %s", (entry_id, user_id))
            existing = cursor.fetchone()
            if existing:
                # Update existing entry
                cursor.execute(
                    "UPDATE journal_entries SET content = %s, mood_score = %s, collection_id = %s WHERE id = %s AND user_id = %s",
                    (content, mood_score, collection_id, entry_id, user_id)
                )
                conn.commit()
                saved_id = entry_id
            else:
                entry_id = None
                
        if not entry_id:
            # Save to database (Insert)
            cursor.execute(
                "INSERT INTO journal_entries (content, mood_score, theme, user_id, collection_id) VALUES (%s, %s, %s, %s, %s)",
                (content, mood_score, 'Default', user_id, collection_id)
            )
            conn.commit()
            saved_id = cursor.lastrowid
            
        conn.close()
        
        return {
            'success': True,
            'message': 'Entry saved successfully',
            'id': saved_id,
            'ai_analysis': ai_result,
            'quote': quote.get('text') if quote else None
        }, 200
        
    except Exception as e:
        return {'success': False, 'message': str(e)}, 500


@app.route('/upload_media', methods=['POST'])
def upload_media():
    if 'user_id' not in session:
        return {"error": "Unauthorized"}, 401
    
    if 'file' not in request.files:
        return {"error": "No file part"}, 400
    
    file = request.files['file']
    if file.filename == '':
        return {"error": "No selected file"}, 400
    
    if file:
        filename = secure_filename(file.filename)
        mimetype = file.mimetype
        user_id = session['user_id']
        file_data = file.read()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_media (user_id, filename, mimetype, media_data) VALUES (%s, %s, %s, %s)",
            (user_id, filename, mimetype, file_data)
        )
        media_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "url": f"/get_media/{media_id}",
            "type": "video" if filename.lower().endswith(('.mp4', '.webm', '.mov')) else "image"
        }

@app.route('/get_media/<int:media_id>')
def get_media(media_id):
    if 'user_id' not in session:
        return "Unauthorized", 401
        
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_media WHERE id = %s AND user_id = %s", (media_id, user_id))
    media = cursor.fetchone()
    conn.close()
    
    if media:
        return send_file(
            io.BytesIO(media['media_data']),
            mimetype=media['mimetype'],
            download_name=media['filename']
        )
    return "Not Found", 404

# --- PWA SERVICE WORKER ROUTE ---
@app.route('/sw.js')
def serve_sw():
    return app.send_static_file('sw.js')


# --- ERROR HANDLERS ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)