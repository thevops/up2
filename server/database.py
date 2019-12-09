import os
import peewee


if os.path.isfile('db.sqlite3'):
    db = peewee.SqliteDatabase('db.sqlite3')
else:
    db = peewee.SqliteDatabase('db.sqlite3')
    Domain.create_table()


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Domain(BaseModel):
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



if __name__ == '__main__':
    # this fragment executes when run explicit: python database.py
    print("Database creating...")
    Domain.create_table()
    print("Done")
