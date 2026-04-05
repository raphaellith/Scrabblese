from peewee import TextField, DoubleField

from models.base_model import BaseModel


class ScrabbleWordEntity(BaseModel):
    # Peewee automatically adds auto-incrementing integer primary key field named id
    text = TextField(unique=True)
    ngrams_probability = DoubleField()