from pathlib import Path

from peewee import SqliteDatabase

PATH_TO_DATABASE: Path = Path(__file__).resolve().with_name("scrabble.db").absolute()

db = SqliteDatabase(PATH_TO_DATABASE, pragmas={
    'journal_mode': 'wal',  # Allow readers while writer active
    'cache_size': -64000,   # 64 MB page cache
    'foreign_keys': 1,      # Enforce FK constraints
})
