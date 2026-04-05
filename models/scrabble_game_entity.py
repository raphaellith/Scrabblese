from peewee import IntegerField, BooleanField, TextField

from models.base_model import BaseModel


class ScrabbleGameEntity(BaseModel):
    # Peewee automatically adds auto-incrementing integer primary key field named id
    cross_tables_game_id = IntegerField(unique=True)
    is_on_list_page = BooleanField()
    gcg_file_contents = TextField()
