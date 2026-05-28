import json
import random
from datetime import datetime, timedelta

import numpy as np
from sklearn.linear_model import LinearRegression

from ..config import MOOD_COLORS
from ..extensions import analyzer, get_db_connection

def analyze_sentiment(content):

    if not content:
        return {"score": 3, "pillar": "peace", "reflection": "What is one truth you've been avoiding today?"}

    vs = analyzer.polarity_scores(content)
    compound = vs['compound']

    if compound >= 0.8:   final_score = 9
    elif compound >= 0.5: final_score = 8
    elif compound >= 0.2: final_score = 7
    elif compound > -0.1: final_score = 5
    elif compound > -0.3: final_score = 4
    elif compound > -0.5: final_score = 3
    elif compound > -0.8: final_score = 2
    else:                 final_score = 1

    text = content.lower()
    pillar = "Peace"
    if any(w in text for w in ['work', 'time', 'manage', 'schedule', 'todo', 'busy', 'deadline']):
        pillar = "Balance"
    elif any(w in text for w in ['learn', 'new', 'goal', 'better', 'future', 'skill', 'try', 'growth']):
        pillar = "Growth"
    elif any(w in text for w in ['health', 'body', 'eat', 'sleep', 'energy', 'feeling', 'wellness']):
        pillar = "Wellness"
    elif any(w in text for w in ['quiet', 'still', 'calm', 'nature', 'breathe', 'meditate', 'peace']):
        pillar = "Peace"

    questions = {
        "Balance":  "Is it the quantity of tasks—or the weight of expectations—that truly feels out of balance today?",
        "Growth":   "What part of this 'new' self are you most afraid to leave behind as you grow?",
        "Wellness": "If your body could speak without using words right now, what's the first thing it would ask for?",
        "Peace":    "In the middle of this quiet moment, what's the one noise you're still trying to ignore?",
    }
    reflection = questions.get(pillar, "What is one truth you've been avoiding today?")
    if final_score >= 4:
        reflection = "This vibrancy feels real—how can you preserve a piece of this light for a darker day?"
    elif final_score <= 2:
        reflection = "When the weight feels this heavy, what is the smallest possible kindness you can show yourself?"

    return {
        "score":      final_score,
        "compound":   compound,
        "pillar":     pillar.lower(),
        "reflection": reflection,
    }

def generate_letter(mood_score, username='friend', content=''):
    name = (username or 'friend').replace('_', ' ').title()

    text = content or ""
    if text.strip().startswith('{') and text.strip().endswith('}'):
        try:
            import json
            data = json.loads(text)
            text = data.get('text', text)
        except Exception:
            pass

    char_sum = sum(ord(c) for c in text)
    index = char_sum % 3

    if mood_score >= 7:
        options = [
            f"Dear {name},\n\nSomething in the way you wrote today felt lighter — more alive. Like you were writing from a place of genuine warmth.\n\nWhatever is filling your days with that feeling, hold onto it gently. Not too tightly, just enough to remember it's there.\n\nI'm glad today was a good one.",
            f"Dear {name},\n\nToday's words carry a brightness to them. There's something lovely about a day that leaves you with something worth writing down.\n\nKeep going. You're doing beautifully.",
            f"Dear {name},\n\nYou wrote today with something that sounded a lot like joy — or maybe just ease. Either way, it looked good on you.\n\nSee you on the next page.",
        ]
    elif mood_score <= 4:
        options = [
            f"Dear {name},\n\nHard days have a weight that's difficult to put into words — and yet here you are, doing just that.\n\nThat takes more courage than you might realize. Writing through the difficult moments is its own kind of bravery.\n\nTomorrow is a fresh page.",
            f"Dear {name},\n\nIt sounds like today asked a lot of you. I hope you're being as gentle with yourself as you deserve.\n\nSome days we write to feel better. Some days we write just to survive them. Both are enough.",
            f"Dear {name},\n\nNot every day is easy, and this one doesn't seem to have been. But you're still here, still writing.\n\nThat matters more than you know. Rest well tonight.",
        ]
    else:
        options = [
            f"Dear {name},\n\nNot every day needs to be extraordinary. Some days are simply lived — and those quiet, steady days are worth remembering too.\n\nThank you for showing up and writing anyway. That says something good about you.",
            f"Dear {name},\n\nThere's something peaceful about a day in the middle. Not too high, not too low — just present.\n\nYou took a moment to reflect, and that's never wasted. See you on the next page.",
            f"Dear {name},\n\nToday was a day. And you wrote about it. That's more than most people do.\n\nSee you tomorrow.",
        ]

    return options[index]


def get_quote_for_entry(content):
    content = content.lower()
    category = 'happy'
    if any(word in content for word in ['sad', 'down', 'cry']):    category = 'sad'
    elif any(word in content for word in ['stress', 'hard', 'exam']): category = 'stressed'

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM quotes WHERE category = %s ORDER BY RAND() LIMIT 1",
        (category,)
    )
    quote = cursor.fetchone()
    conn.close()
    return quote

def calculate_mood_trend(entries):
    if len(entries) < 2:
        return {"status": "Seeding", "slope": 0, "msg": "The pages are fresh.", "consistency": "Write your first entry."}

    X = np.array(range(len(entries))).reshape(-1, 1)
    y = []
    for e in reversed(entries):
        val = e.get('mood_score', 5) / 4.5 - 1.0
        if e.get('content'):
            try:
                text = e['content']
                if isinstance(text, str) and (text.startswith('{') or text.startswith('[')):
                    text = json.loads(text).get('text', text)
                val = analyzer.polarity_scores(text)['compound']
            except Exception:
                pass
        y.append(val)

    y = np.array(y)
    model = LinearRegression().fit(X, y)
    slope = model.coef_[0]

    status = "Bluming" if slope > 0.05 else "Cloudy" if slope < -0.05 else "Steady"
    return {
        "status":      status,
        "slope":       round(slope, 4),
        "msg":         f"Your emotional rhythm is {status}.",
        "consistency": "Consistent.",
    }

def calculate_advanced_insights(entries):
    if len(entries) < 3:
        return None

    X_words, X_time, y_scores = [], [], []

    for e in entries:
        content = e.get('content', '')
        if content.startswith('{'):
            try:
                content = json.loads(content).get('text', '')
            except Exception:
                pass

        word_count = len(content.split())
        hour = e['entry_date'].hour + (e['entry_date'].minute / 60)
        score = (e.get('mood_score', 5) - 1) / 8.0

        X_words.append([word_count])
        X_time.append([hour])
        y_scores.append(score)

    y_scores = np.array(y_scores)
    word_slope = LinearRegression().fit(np.array(X_words), y_scores).coef_[0]
    time_slope = LinearRegression().fit(np.array(X_time), y_scores).coef_[0]

    X_trend    = np.array(range(len(entries))).reshape(-1, 1)
    prediction = LinearRegression().fit(X_trend, y_scores).predict([[len(entries) + 1]])[0]

    word_insight = "Longer entries correlate with better clarity." if word_slope > 0.001 else "Your mood stays stable regardless of length."
    time_insight = (
        "Your energy peaks in the evening." if time_slope > 0.01
        else "Morning reflections bring you more peace." if time_slope < -0.01
        else "Your mood is consistent throughout the day."
    )

    return {
        "word_slope":       round(word_slope * 100, 2),
        "word_msg":         word_insight,
        "time_msg":         time_insight,
        "predicted_energy": round(prediction * 100, 1),
        "predicted_label":  "High" if prediction > 0.7 else "Moderate" if prediction > 0.4 else "Restorative",
    }

def get_memory_entry(entries):
    if not entries:
        return None
    today = datetime.now().date()
    candidates = [
        (365, 10, "A year ago"),
        (182,  7, "Six months ago"),
        (30,   5, "A month ago"),
        (7,    2, "Last week"),
    ]
    for days, window, label in candidates:
        target = today - timedelta(days=days)
        cutoff = target - timedelta(days=window)
        for e in entries:
            entry_date = e['entry_date'].date()
            if entry_date < cutoff:
                break
            if abs((entry_date - target).days) <= window:
                text    = get_preview_text(e.get('content', ''))
                preview = (text[:120].rsplit(' ', 1)[0] + '…') if len(text) > 120 else text
                return {
                    'label':      label,
                    'date':       e['entry_date'].strftime("%B %d, %Y"),
                    'preview':    preview,
                    'mood_label': e.get('mood_label', 'Steady'),
                    'mood_color': MOOD_COLORS.get(e.get('mood_score', 5), "#DFDAC9"),
                    'id':         e['id'],
                }
    return None

def calculate_energy_data(content):
    if not content:
        return {"score": 50, "mood": "neutral", "label": "Resting", "color": "#F5C842"}

    c = content.lower()
    high = ['excited', 'amazing', 'great', 'love', 'happy', 'bloom', 'wonderful', 'active']
    low  = ['tired', 'exhausted', 'sad', 'bad', 'lonely', 'drain', 'heavy', 'storm']

    score = 50
    if any(word in c for word in high): score += 30
    if any(word in c for word in low):  score -= 30
    if len(c) > 200:                    score += 10
    score = max(0, min(100, score))

    if score >= 80:
        return {"score": score, "mood": "high",     "label": "Happy",   "color": "#5BB8F5", "light": "#98D3F5", "dark": "#2A88BF", "mouth": "M3 3 Q11 12 19 3"}
    elif score >= 60:
        return {"score": score, "mood": "balanced", "label": "Calm",    "color": "#6DBF8A", "light": "#9DDBB0", "dark": "#3A8A56", "mouth": "M3 6 Q11 2 19 6"}
    elif score >= 40:
        return {"score": score, "mood": "neutral",  "label": "Neutral", "color": "#F5C842", "light": "#FAE092", "dark": "#BF9210", "mouth": "M4 5 L18 5"}
    elif score >= 20:
        return {"score": score, "mood": "low",      "label": "Sad",     "color": "#E87FA0", "light": "#FFAAC4", "dark": "#B54A6E", "mouth": "M3 3 Q11 9 19 3"}
    else:
        return {"score": score, "mood": "drained",  "label": "Stressed","color": "#A99BC4", "light": "#C4B5E8", "dark": "#7E6BA9", "mouth": "M5 3 Q11 3 17 3"}

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
    now      = datetime.now()
    week_ago = now - timedelta(days=7)

    recent_entries = [e for e in entries if e['entry_date'] >= week_ago]
    active_days    = len(set(e['entry_date'].date() for e in recent_entries))
    total_entries  = len(recent_entries)

    total_words = 0
    for e in recent_entries:
        content = e.get('content', '')
        if content.startswith('{'):
            try:
                content = json.loads(content).get('text', '')
            except Exception:
                pass
        total_words += len(content.split())

    total_minutes = total_words // 40
    seconds       = int(((total_words / 40) - total_minutes) * 60)

    return {
        "date_range":   f"{week_ago.strftime('%d %b')} - {now.strftime('%d %b')}",
        "days":         active_days,
        "entries":      total_entries,
        "minutes":      total_minutes,
        "seconds":      seconds,
        "days_dir":     "up" if active_days >= 3 else "down",
        "entries_dir":  "up" if total_entries >= 3 else "down",
        "time_dir":     "down" if total_minutes < 5 else "up",
    }

def get_preview_text(content):
    if not content:
        return ""
    if content.strip().startswith('{') and content.strip().endswith('}'):
        try:
            data = json.loads(content)
            if 'text' in data:
                return data['text'].strip().replace('\n', ' ')
        except Exception:
            pass
    return content.strip().replace('\n', ' ')
