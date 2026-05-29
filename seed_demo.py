"""
MoodBlume — Demo Seed Script
Inserts 4 journal entries (one per mood) spread across 4 months.
Run: python seed_demo.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from moodblume.extensions import get_db_connection
from moodblume.ai.helpers import analyze_sentiment

# ── CONFIG ─────────────────────────────────────────────────────────────────────
# Change this to your actual username if needed
TARGET_USERNAME = None   # None = use the first user found in DB
# ───────────────────────────────────────────────────────────────────────────────

ENTRIES = [
    {
        "date": "2025-02-14",
        "label": "JOY",
        "content": "Today was absolutely wonderful. I woke up feeling refreshed and grateful for everything around me. The morning light came through the window in a way that felt almost golden, and I just sat with my coffee and smiled. I love days like this — full of warmth, laughter, and possibility. Everything feels hopeful and bright."
    },
    {
        "date": "2025-03-08",
        "label": "CALM",
        "content": "A quiet Saturday. I tidied up my room, made some tea, and sat by the window for a while. Nothing extraordinary happened, but there was a soft, gentle feeling to the day. The kind of day where everything feels okay. I feel at ease, rested, and content. It was nice."
    },
    {
        "date": "2025-04-22",
        "label": "SADNESS",
        "content": "I've been feeling really low lately. I miss the people I used to be close to, and I can't shake this heavy feeling. Everything feels distant and a little grey. I cried this evening without really knowing why. I'm trying to be kind to myself but it's hard when I feel this lonely and tired."
    },
    {
        "date": "2025-05-03",
        "label": "ANGER",
        "content": "I am so furious and frustrated right now. Everything went wrong today and I hate feeling this powerless. I'm enraged at how unfair and horrible this situation has been. I can't stand it. It's awful and I'm exhausted from pretending it's okay. I feel terrible and I'm not fine at all."
    },
]

def main():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Find user
    if TARGET_USERNAME:
        cursor.execute("SELECT id, username FROM users WHERE username = %s LIMIT 1", (TARGET_USERNAME,))
    else:
        cursor.execute("SELECT id, username FROM users ORDER BY id ASC LIMIT 1")
    user = cursor.fetchone()

    if not user:
        print("❌  No user found. Make sure you have an account.")
        return

    user_id = user['id']
    print(f"✅  Using account: {user['username']} (id={user_id})")

    # Find their most recent collection
    cursor.execute(
        "SELECT id, name FROM collections WHERE user_id = %s ORDER BY created_at DESC LIMIT 1",
        (user_id,)
    )
    col = cursor.fetchone()
    collection_id = col['id'] if col else None
    print(f"✅  Journal: {col['name'] if col else 'None (entries will be uncollected)'} (id={collection_id})")

    inserted = 0
    for e in ENTRIES:
        sentiment = analyze_sentiment(e['content'])
        score = sentiment['score']

        cursor.execute(
            """INSERT INTO journal_entries (content, mood_score, theme, user_id, collection_id, entry_date)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (e['content'], score, 'Default', user_id, collection_id, e['date'])
        )
        print(f"  📝  [{e['label']}] {e['date']} → mood_score={score}")
        inserted += 1

    conn.commit()
    conn.close()
    print(f"\n✅  {inserted} demo entries inserted successfully!")
    print("   Refresh /archive to see them in all collection views.\n")

if __name__ == '__main__':
    main()
