from peewee import ForeignKeyField, CompositeKey, IntegerField

from models.base_model import BaseModel
from models.scrabble_game_entity import ScrabbleGameEntity
from models.scrabble_word_entity import ScrabbleWordEntity


class ScrabbleGameWordEntity(BaseModel):
    # When a ScrabbleGameEntity or ScrabbleWordEntity is deleted, all related ScrabbleGameWordEntities are also deleted
    scrabble_game_id = ForeignKeyField(ScrabbleGameEntity, backref='words', on_delete='CASCADE')
    scrabble_word_id = ForeignKeyField(ScrabbleWordEntity, backref='games', on_delete='CASCADE')
    count = IntegerField(default=0)

    class Meta:
        primary_key = CompositeKey('scrabble_game_id', 'scrabble_word_id')