from peewee import Model, SqliteDatabase

PATH_TO_DATABASE: str = './scrabble.db'

db = SqliteDatabase(PATH_TO_DATABASE, pragmas={
    'journal_mode': 'wal',  # Allow readers while writer active
    'cache_size': -64000,   # 64 MB page cache
    'foreign_keys': 1,      # Enforce FK constraints
})

class BaseModel(Model):
    """
    The base model from which all models inherit in order to share the database connection.
    """
    class Meta:
        database = db
