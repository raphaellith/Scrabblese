from peewee import ForeignKeyField, CompositeKey, IntegerField

from Scrabble.model.BaseModel import BaseModel
from Scrabble.model.ScrabbleGameEntity import ScrabbleGameEntity
from Scrabble.model.ScrabbleWordEntity import ScrabbleWordEntity


class ScrabbleGameWordEntity(BaseModel):
    scrabble_game_id = ForeignKeyField(ScrabbleGameEntity, backref='words')
    scrabble_word_id = ForeignKeyField(ScrabbleWordEntity, backref='games')
    count = IntegerField(default=0)

    class Meta:
        primary_key = CompositeKey('scrabble_game_id', 'scrabble_word_id')