from peewee import Model, SqliteDatabase

from models.scrabble_game_entity import ScrabbleGameEntity
from models.scrabble_game_word_entity import ScrabbleGameWordEntity
from models.scrabble_word_entity import ScrabbleWordEntity

PATH_TO_DATABASE: str = './scrabble.db'

db = SqliteDatabase(PATH_TO_DATABASE, pragmas={
    'journal_mode': 'wal',  # Allow readers while writer active
    'cache_size': -64000,   # 64 MB page cache
    'foreign_keys': 1,      # Enforce FK constraints
})


def initialise_database():
    """
    Ensures all Scrabble cache tables exist.
    :return: None
    """
    db.connect(reuse_if_open=True)
    db.create_tables([ScrabbleGameEntity, ScrabbleWordEntity, ScrabbleGameWordEntity], safe=True)


class BaseModel(Model):
    """
    The base model from which all models inherit in order to share the database connection.
    """
    class Meta:
        database = db
