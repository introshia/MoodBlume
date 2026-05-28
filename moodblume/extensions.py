import mysql.connector
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from .config import DB_CONFIG

analyzer = SentimentIntensityAnalyzer()

def get_db_connection():

    return mysql.connector.connect(**DB_CONFIG)
