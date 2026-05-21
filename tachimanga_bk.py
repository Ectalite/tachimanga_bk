import gzip
import json
from zipfile import ZipFile
import sqlite3
from google.protobuf.json_format import Parse
from schema_pb2 import Backup

with ZipFile('examples/Tachimanga_backup_2026-05-16_00-40-22-106.zip', 'r') as zf:
    with ZipFile(zf.open('contents.zip'), 'r') as content_file:
        content_file.extract('tachimanga.db', path='./tmp')
conn = sqlite3.connect('./tmp/tachimanga.db')
cursor = conn.cursor()

# Get all manga in library
cursor.execute("""
                SELECT id, source, url, title, artist, author, description, genre, status, thumbnail_url, in_library_at
                FROM Manga
                WHERE in_library = 1;
                """)
manga_rows = cursor.fetchall()

backup_manga = []

for manga_row in manga_rows:
    manga_id = manga_row[0]  # id is the first column

    # Get chapters for this manga
    cursor.execute("""
                    SELECT url, name, scanlator, fetched_at, date_upload, chapter_number, "read", last_page_read
                    FROM Chapter
                    WHERE manga = ?;
                    """, (manga_id,))
    chapter_rows = cursor.fetchall()

    # Format chapters
    chapters = []
    for chapter_row in chapter_rows:
        chapters.append({
            "url": chapter_row[0],
            "name": chapter_row[1],
            "scanlator": chapter_row[2],
            "read": bool(chapter_row[6]),
            "lastPageRead": str(chapter_row[7]),
            "dateFetch": str(chapter_row[3]),
            "dateUpload": str(chapter_row[4]),
            "chapterNumber": chapter_row[5]
        })

    # Format manga
    manga_data = {
        "source": str(manga_row[1]),
        "url": manga_row[2],
        "title": manga_row[3],
        "artist": manga_row[4],
        "author": manga_row[5],
        "description": manga_row[6],
        "status": manga_row[8],
        "thumbnailUrl": manga_row[9],
        "dateAdded": str(manga_row[10]),
        "chapters": chapters
    }
    if manga_row[7] is not None:
        manga_data["genre"] = [manga_row[7]]

    cursor.execute("""
                    SELECT category
                    FROM CategoryManga
                    WHERE manga = ?;
                   """, (manga_id,))
    category_rows = cursor.fetchall()
    manga_categories = []
    for row in category_rows:
        manga_categories += str(row[0])
    if manga_categories:
        manga_data["categories"] = manga_categories

    backup_manga.append(manga_data)

#Backup categories
cursor.execute("""
                SELECT name, "order"
                FROM Category;
               """)
category_rows = cursor.fetchall()
category_data = []
for category in category_rows:
    category_data.append({
        "name": category[0],
        "order": category[1]
    })

#Backup sources
cursor.execute("""
                SELECT name, id
                FROM Source;
               """)
source_rows = cursor.fetchall()
source_data = []
for source in source_rows:
    source_data.append({
        "name": source[0],
        "sourceId": source[1]
    })

# Final JSON
result = {"backupManga": backup_manga, "backupCategories": category_data, "backupSources": source_data}

# Print or save the JSON
#print(json.dumps(result, indent=2, ensure_ascii=False))

# Optionally, save to a file:
with open('backup_manga.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

with gzip.open('backup.tachibk', 'wb') as w:
    w.write(Parse(json.dumps(result), Backup()).SerializeToString())