import sys
sys.path.insert(0, '/Users/dannamayd.desear/Documents/MoodBlume')
from app import app, get_db_connection

conn = get_db_connection()
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT id, username FROM users LIMIT 1")
user = cursor.fetchone()
conn.close()

if user:
    user_id = user['id']
    username = user['username']
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['user_id'] = user_id
        sess['username'] = username
    res = client.get('/archive')
    print(res.data.decode('utf-8'))
else:
    print("No user found")
