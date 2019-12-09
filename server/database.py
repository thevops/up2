import peewee
import os

DB_EXISTS = False

if os.path.isfile('db.sqlite3'):
    DB_EXISTS = True


db = peewee.SqliteDatabase('db.sqlite3')


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


if not DB_EXISTS:
    print("Database empty... creating tables")
    Domain.create_table()



if __name__ == '__main__':
    domains = Domain.select()

    response_data = {}
    for i in domains:
        response_data[i.id] = {"name": i.name, "token": i.token}

    print(response_data)


