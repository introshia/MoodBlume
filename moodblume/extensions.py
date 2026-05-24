import mysql.connector
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from .config import DB_CONFIG

# ── Shared VADER sentiment analyser (initialised once at startup) ─────────────
analyzer = SentimentIntensityAnalyzer()


def get_db_connection():
    """Return a new MySQL connection using the central DB_CONFIG."""
    return mysql.connector.connect(**DB_CONFIG)
