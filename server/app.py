
import secrets

from flask import Flask, render_template
from database import db, Domain


app = Flask(__name__)


db.connect()


@app.route('/init', methods=['POST'])
def init():
    # get data from form
    try:
        new_domain = request.form['domain']
    except:
        return "", 400 # Bad Request

    # check if domain exists
    domain = Domain.select().where(Domain.name == new_domain).get()
    if domain:
        return "Domain exists", 400
    else:
        # generate token
        token = secrets.token_hex(16)

        # add domain to database
        with db.transaction():
            try:
                d = Domain(name=new_domain, token=token)
                d.save()
            except:
                db.rollback()
                return "Server error", 500

        # success - return token to user
        return token, 200



if __name__ == '__main__':
    app.run('127.0.0.1', debug=True) # start aplikacji, polaczenie do lokalnego hosta, wlaczenie pokazywania bledow
