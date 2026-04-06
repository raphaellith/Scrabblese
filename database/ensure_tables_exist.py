from database.initialisation import db
from models.scrabble_game_entity import ScrabbleGameEntity
from models.scrabble_game_word_entity import ScrabbleGameWordEntity
from models.scrabble_word_entity import ScrabbleWordEntity


def initialise_database():
    """
    Ensures all Scrabble cache tables exist.
    :return: None
    """
    db.connect(reuse_if_open=True)
    db.create_tables([ScrabbleGameEntity, ScrabbleWordEntity, ScrabbleGameWordEntity], safe=True)