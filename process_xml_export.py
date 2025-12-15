"""
Process ClipMate XML export and populate SQLite database
Pure XML-based approach - no binary file parsing needed
"""
import os
import sqlite3
from clipmate_xml_parser import ClipMateXMLParser

def create_database(db_path):
    """Create or recreate the clips database with enhanced schema"""
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create clips table with all XML fields
    cursor.execute('''
        CREATE TABLE clips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guid TEXT UNIQUE,
            collid TEXT,
            title TEXT,
            creator TEXT,
            created_at TEXT,
            modified_at TEXT,
            sourceurl TEXT,
            shortcut TEXT,
            locale TEXT,
            icons TEXT,
            encrypted TEXT,
            macro TEXT,
            viewtab TEXT,
            content_text TEXT,
            content_html BLOB,
            content_image BLOB,
            size INTEGER,
            format_list TEXT,
            source_xml TEXT
        )
    ''')

    # Create collections table
    cursor.execute('''
        CREATE TABLE collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guid TEXT UNIQUE,
            title TEXT,
            parent TEXT,
            lmtype TEXT,
            listtype TEXT,
            ilindex TEXT,
            retentionlimit TEXT,
            newclipsgo TEXT,
            acceptnewclips TEXT,
            acceptduplicates TEXT,
            sortcolumn TEXT,
            sortascending TEXT,
            encrypted TEXT,
            sortkey TEXT,
            favorite TEXT,
            sql TEXT
        )
    ''')

    # Create indexes for common queries
    cursor.execute('CREATE INDEX idx_clips_guid ON clips(guid)')
    cursor.execute('CREATE INDEX idx_clips_created ON clips(created_at)')
    cursor.execute('CREATE INDEX idx_clips_creator ON clips(creator)')
    cursor.execute('CREATE INDEX idx_clips_title ON clips(title)')
    cursor.execute('CREATE INDEX idx_collections_guid ON collections(guid)')

    conn.commit()
    print(f"Created database: {db_path}")
    return conn


def insert_collections(conn, collections):
    """Insert collections into database"""
    cursor = conn.cursor()

    for coll in collections:
        cursor.execute('''
            INSERT INTO collections (
                guid, title, parent, lmtype, listtype, ilindex,
                retentionlimit, newclipsgo, acceptnewclips, acceptduplicates,
                sortcolumn, sortascending, encrypted, sortkey, favorite, sql
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            coll.get('id'),
            coll.get('title'),
            coll.get('parent'),
            coll.get('lmtype'),
            coll.get('listtype'),
            coll.get('ilindex'),
            coll.get('retentionlimit'),
            coll.get('newclipsgo'),
            coll.get('acceptnewclips'),
            coll.get('acceptduplicates'),
            coll.get('sortcolumn'),
            coll.get('sortascending'),
            coll.get('encrypted'),
            coll.get('sortkey'),
            coll.get('favorite'),
            coll.get('sql')
        ))

    conn.commit()
    print(f"Inserted {len(collections)} collections")


def insert_clips(conn, clips, source_xml):
    """Insert clips into database"""
    cursor = conn.cursor()

    inserted = 0
    skipped = 0

    for clip in clips:
        # Build format list string
        format_list = ', '.join([f.get('format', 'Unknown') for f in clip.get('formats', [])])

        try:
            cursor.execute('''
                INSERT INTO clips (
                    guid, collid, title, creator, created_at, modified_at,
                    sourceurl, shortcut, locale, icons, encrypted, macro, viewtab,
                    content_text, content_html, content_image, size, format_list, source_xml
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                clip.get('id'),
                clip.get('collid'),
                clip.get('title'),
                clip.get('creator'),
                clip.get('created_at'),
                clip.get('modified_at'),
                clip.get('sourceurl'),
                clip.get('shortcut'),
                clip.get('locale'),
                clip.get('icons'),
                clip.get('encrypted'),
                clip.get('macro'),
                clip.get('viewtab'),
                clip.get('content_text'),
                clip.get('content_html'),
                clip.get('content_image'),
                clip.get('size'),
                format_list,
                source_xml
            ))
            inserted += 1

        except sqlite3.IntegrityError:
            # Duplicate GUID - skip
            skipped += 1

    conn.commit()
    print(f"Inserted {inserted} clips ({skipped} skipped as duplicates)")


def main():
    """Main processing function"""
    base_dir = r"C:\myStuff\ParseClipmate"
    xml_file = os.path.join(base_dir, "ClipMate_Export_MYDESK_My Clips_2025-12-15_045940.xml")
    db_path = os.path.join(base_dir, "clipmate_from_xml.db")

    print("="*80)
    print("ClipMate XML Export to SQLite Database")
    print("="*80)
    print(f"Source XML: {xml_file}")
    print(f"Target DB: {db_path}")
    print()

    if not os.path.exists(xml_file):
        print(f"ERROR: XML file not found: {xml_file}")
        return

    # Parse XML
    print("Parsing XML export...")
    parser = ClipMateXMLParser(xml_file)
    parser.load()

    collections = parser.parse_collections()
    clips = parser.parse_clips()

    print(f"Found {len(collections)} collections")
    print(f"Found {len(clips)} clips")
    print()

    # Create database
    conn = create_database(db_path)

    # Insert data
    insert_collections(conn, collections)
    insert_clips(conn, clips, os.path.basename(xml_file))

    # Verify
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM collections")
    coll_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM clips")
    clip_count = cursor.fetchone()[0]

    print()
    print("="*80)
    print("DATABASE VERIFICATION")
    print("="*80)
    print(f"Collections in database: {coll_count}")
    print(f"Clips in database: {clip_count}")

    # Sample query
    cursor.execute('''
        SELECT guid, title, creator, created_at, format_list
        FROM clips
        ORDER BY created_at DESC
        LIMIT 5
    ''')

    print("\nMost recent 5 clips:")
    for row in cursor.fetchall():
        guid, title, creator, created, formats = row
        print(f"  {created} | {creator:20s} | {title[:40]}")
        print(f"    GUID: {guid}")
        print(f"    Formats: {formats}")

    # Statistics by creator
    cursor.execute('''
        SELECT creator, COUNT(*) as count
        FROM clips
        GROUP BY creator
        ORDER BY count DESC
        LIMIT 10
    ''')

    print("\nTop 10 Creators:")
    for row in cursor.fetchall():
        creator, count = row
        print(f"  {creator}: {count}")

    # Statistics by format
    cursor.execute('''
        SELECT format_list, COUNT(*) as count
        FROM clips
        GROUP BY format_list
        ORDER BY count DESC
        LIMIT 10
    ''')

    print("\nTop 10 Format Combinations:")
    for row in cursor.fetchall():
        formats, count = row
        print(f"  {formats}: {count}")

    conn.close()

    print()
    print("="*80)
    print("SUCCESS - Database created and populated from XML export")
    print("="*80)
    print(f"Database location: {db_path}")
    print(f"Total clips: {clip_count}")
    print(f"Total collections: {coll_count}")
    print()
    print("Next steps:")
    print("  1. Update server.py to use clipmate_from_xml.db")
    print("  2. Test web interface with new database")
    print("  3. Compare results with binary parsing approach")


if __name__ == "__main__":
    main()
