import peewee


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



if __name__ == '__main__':
    # this fragment executes when run explicit: python database.py
    print("Database checking...")
    db.connect()
    try:
        query = Domain.select()
        if not query.exists():
            print("Database empty... creating tables")
            Domain.create_table()
            print("Done")
    except Exception as e:
        print("Error", e)
        print("Database empty... creating tables")
        Domain.create_table()
        print("Done")

    print("Checking again...")
    try:
        query = Domain.select()
        if query.exists():
            print(query)
    except Exception as e:
        print("Error", e)
        exit(1)


