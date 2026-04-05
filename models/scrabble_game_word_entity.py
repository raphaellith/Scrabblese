from peewee import ForeignKeyField, CompositeKey, IntegerField

from models.base_model import BaseModel
from models.scrabble_game_entity import ScrabbleGameEntity
from models.scrabble_word_entity import ScrabbleWordEntity


class ScrabbleGameWordEntity(BaseModel):
    scrabble_game_id = ForeignKeyField(ScrabbleGameEntity, backref='words')
    scrabble_word_id = ForeignKeyField(ScrabbleWordEntity, backref='games')
    count = IntegerField(default=0)

    class Meta:
        primary_key = CompositeKey('scrabble_game_id', 'scrabble_word_id')