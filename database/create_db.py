import sqlite3

def create_db():
    connection = sqlite3.Connection('database.db')
    cursor = sqlite3.Cursor(connection)
    cursor.execute('CREATE TABLE transcriptions (id INTEGER PRIMARY KEY AUTOINCREMENT , file_name TEXT, audio_file_name TEXT, transcription LONGTEXT, date_created DATE)')
    cursor.execute('CREATE TABLE features (id INTEGER PRIMARY KEY, keywords LONGTEXT, FOREIGN KEY (id) REFERENCES transcriptions(id))')
    cursor.execute('CREATE TABLE report (id INTEGER PRIMARY KEY, background LONGTEXT, summary LONGTEXT, reflection LONGTEXT, conclusion LONGTEXT, FOREIGN KEY (id) REFERENCES transcriptions(id))')
    connection.close()

if __name__ == "__main__":
    create_db()
