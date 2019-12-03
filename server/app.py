
import secrets
import os
from zipfile import ZipFile
import shutil

from flask import Flask, render_template, request, jsonify
from database import db, Domain


################################    SETTINGS    ################################

UPLOAD_DIRECTORY = 'uploads'
DOMAINS_DIRECTORY = 'domains/'


################################    FLASK, DB connection    ################################

app = Flask(__name__)

db.connect()


################################    AUXILIARY    ################################

def authorization(domain, token):
    # get token from db
    try:
        d = Domain.select().where(Domain.name == domain).get()
    except:
        return "Domain not initialized", 400, None

    # check if token matches
    if d.token != token:
        return "Token does not match to domain", 401, None

    # return success and domain object
    return "Success", 200, d


################################    ROUTING    ################################


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


@app.route('/deploy', methods=['POST'])
def deploy():
    # prepare response
    response_data = {}
    # get form
    try:
        token = request.form['token']
        domain = request.form['domain']
        file = request.files['file']
    except:
        response_data = {"status": "Client error"}
        return jsonify(response_data), 400 # Bad Request

    # authorization
    status, error_code, _ = authorization(domain, token)
    if error_code != 200:
        response_data = {"status": status}
        return jsonify(response_data), error_code

    # save file
    if file.filename != '':
        file.save(os.path.join(UPLOAD_DIRECTORY, file.filename))


    domain_dir = DOMAINS_DIRECTORY + "/" + domain + "/"
    # create domain directory
    try:
        shutil.rmtree(domain_dir)
        os.mkdir(domain_dir)
    except:
        pass

    # unzip package in domain directory
    try:
        with ZipFile(UPLOAD_DIRECTORY + '/' + domain + '.zip', 'r') as zip_obj:
            zip_obj.extractall(domain_dir)
    except:
        response_data = {"status": "Unzip domain package error"}
        return jsonify(response_data), 500

    # reload nginx ???

    response_data = {"status":"Success"}
    return jsonify(response_data), 200


@app.route('/delete', methods=['POST'])
def delete():
    # prepare response
    response_data = {}
    # get form
    try:
        token = request.form['token']
        domain = request.form['domain']
    except:
        response_data = {"status": "Client error"}
        return jsonify(response_data), 400 # Bad Request

    # authorization
    status, error_code, domain_obj = authorization(domain, token)
    if error_code != 200:
        response_data = {"status": status}
        return jsonify(response_data), error_code


    # delete directory
    domain_dir = DOMAINS_DIRECTORY + "/" + domain + "/"
    # create domain directory
    try:
        shutil.rmtree(domain_dir)
    except:
        response_data = {"status": "Removing domain directory error"}
        return jsonify(response_data), 500
    # delete nginx vhost

    # delete Domain object in database
    try:
        domain_obj.delete_instance()
    except:
        response_data = {"status": "Removing domain in database error"}
        return jsonify(response_data), 500

    # return successful response
    response_data = {"status": "Success"}
    return jsonify(response_data), 200



if __name__ == '__main__':
    app.run('127.0.0.1', debug=True) # start aplikacji, polaczenie do lokalnego hosta, wlaczenie pokazywania bledow
