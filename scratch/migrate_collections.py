from moodblume.extensions import get_db_connection

def migrate():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if paper_type already exists
    cursor.execute("SHOW COLUMNS FROM collections LIKE 'paper_type'")
    if not cursor.fetchone():
        print("Adding paper_type column...")
        cursor.execute("ALTER TABLE collections ADD COLUMN paper_type VARCHAR(20) DEFAULT 'lined'")
        
    # Check if page_type already exists
    cursor.execute("SHOW COLUMNS FROM collections LIKE 'page_type'")
    if not cursor.fetchone():
        print("Adding page_type column...")
        cursor.execute("ALTER TABLE collections ADD COLUMN page_type VARCHAR(20) DEFAULT 'endless'")
        
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == '__main__':
    migrate()
