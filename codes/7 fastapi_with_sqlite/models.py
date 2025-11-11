import sqlite3
print('creating tables...')
def create_tables():
    conn = sqlite3.connect('app.db')
    cur = conn.cursor()
    cur.execute("""
    create table if not exists users (
        id integer primary key autoincrement,
        username text unique not null,
        email text unique not null,
        full_name text             
    )
    """)
    conn.commit()
    conn.close()
    print('Tables created successfully')