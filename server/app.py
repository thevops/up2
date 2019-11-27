
import secrets

from flask import Flask, render_template, request, jsonify
from database import db, Domain


app = Flask(__name__)


db.connect()


@app.route('/init', methods=['POST'])
def init():
    # prepare response
    response_data = {}
    # get data from form
    try:
        new_domain = request.form['domain']
    except:
        response_data = {"status": "Client error"}
        return jsonify(response_data), 400 # Bad Request

    # check if domain exists
    try:
        domain = Domain.select().where(Domain.name == new_domain).get()
        response_data = {"status": "Domain exists"}
        return jsonify(response_data), 400
    except:
        # domain not exists, so you can use it
        # generate token
        token = secrets.token_hex(16)

        # add domain to database
        with db.transaction():
            try:
                d = Domain(name=new_domain, token=token)
                d.save()
            except:
                db.rollback()
                response_data = {"status": "Server error"}
                return jsonify(response_data), 500

        # success - return token to user
        response_data = {"status":"Success", "token": token}
        return jsonify(response_data), 200



if __name__ == '__main__':
    app.run('127.0.0.1', debug=True) # start aplikacji, polaczenie do lokalnego hosta, wlaczenie pokazywania bledow
