"""
app.py — Entry point for MoodBlume.
All application logic lives in the moodblume/ package.
"""
from moodblume import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5001)