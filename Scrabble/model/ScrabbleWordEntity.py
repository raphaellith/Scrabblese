from peewee import TextField, DoubleField

from Scrabble.model.BaseModel import BaseModel


class ScrabbleWordEntity(BaseModel):
    # Peewee automatically adds auto-incrementing integer primary key field named id
    text = TextField(unique=True)
    ngrams_probability = DoubleField()