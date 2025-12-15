import sqlite3
import os

class ClipmateDB:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clips (
                id INTEGER PRIMARY KEY,
                guid TEXT,
                title TEXT,
                creator TEXT,
                url TEXT,
                created_at TIMESTAMP,
                content_text TEXT,
                content_image BLOB,
                source_archive TEXT,
                size INTEGER,
                native_id INTEGER
            )
        ''')
        self.conn.commit()

    def insert_clip(self, clip_data, source_archive="live"):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO clips (guid, title, creator, url, content_text, source_archive, created_at, size, native_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            clip_data.get('guid'), 
            clip_data.get('title'), 
            clip_data.get('creator'), 
            clip_data.get('url'),
            clip_data.get('content_text'),
            source_archive,
            clip_data.get('created_at'),
            clip_data.get('size'),
            clip_data.get('native_id')
        ))
        self.conn.commit()
        return cursor.lastrowid

    def close(self):
        if self.conn:
            self.conn.close()
