import os

# ── Mood colour palette (score 1–9) ──────────────────────────────────────────
MOOD_COLORS = {
    9: "#F2DD66", 8: "#FFB4D1", 7: "#85D0E8", 6: "#A8DADC",
    5: "#DFDAC9", 4: "#C5C6D0", 3: "#B6AEE6", 2: "#A8C1ED", 1: "#FF9AA2",
}

# ── Database connection settings ─────────────────────────────────────────────
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': os.getenv('DB_PASSWORD'),
    'database': 'moodblume_db',
}
