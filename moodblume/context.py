from flask import session
from .extensions import get_db_connection

def register_context_processors(app):

    @app.context_processor
    def inject_sidebar_data():
        user_id = session.get('user_id')
        if not user_id:
            return {}
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM collections WHERE user_id = %s ORDER BY created_at DESC",
                (user_id,)
            )
            collections = cursor.fetchall()
            conn.close()
            return {'user_collections': collections}
        except Exception:
            return {'user_collections': []}
