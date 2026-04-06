from peewee import Model

from database.initialisation import db


class BaseModel(Model):
    """
    The base model from which all models inherit in order to share the database connection.
    """
    class Meta:
        database = db
