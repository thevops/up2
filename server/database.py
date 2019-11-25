import peewee

from flask import jsonify


db = peewee.SqliteDatabase('db.sqlite3')



class BaseModel(peewee.Model):
    class Meta:
        database = db


class User(BaseModel):
    name = peewee.CharField(unique=True)
    token = peewee.CharField(unique=True)

    @property
    def serialize(self):
        data = {
            'id': self.id,
            'name': self.name,
            'token': self.token
        }
        return data




