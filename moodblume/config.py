import os

MOOD_COLORS = {
    9: "#F2DD66", 8: "#FFB4D1", 7: "#85D0E8", 6: "#A8DADC",
    5: "#DFDAC9", 4: "#C5C6D0", 3: "#B6AEE6", 2: "#A8C1ED", 1: "#FF9AA2",
}

DB_CONFIG = {
    'host': os.getenv('MYSQLHOST', 'localhost'),
    'port': int(os.getenv('MYSQLPORT', 3306)),
    'user': os.getenv('MYSQLUSER', 'root'),
    'password': os.getenv('MYSQLPASSWORD', os.getenv('DB_PASSWORD')),
    'database': os.getenv('MYSQLDATABASE', 'moodblume_db'),
}
