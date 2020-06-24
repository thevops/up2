import secrets
import os
import sys
from zipfile import ZipFile
import shutil

from flask import Flask, render_template, request, jsonify

from tinydb import TinyDB, Query, where


################################    SETTINGS    ################################

UPLOAD_DIRECTORY = 'uploads' # contains zip files after upload
DOMAINS_DIRECTORY = 'domains' # contains unzipped files of webiste
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
os.makedirs(DOMAINS_DIRECTORY, exist_ok=True)


################################     FLASK     ################################

app = Flask(__name__)


################################     DB     ################################

# schema:
# { "domain": "token", ... }

try:
    db = TinyDB('db.json')
    db.default_table_name = 'domains'
except:
    print("db.json error")
    sys.exit(1)


################################    AUXILIARY    ################################


################    Database    ################


def get_domain(domain):
    Domain = Query()
    try:
        d = db.search(Domain.domain == domain)[0] # it's list so get only first element
    except:
        return False, None # not exists

    if d:
        return d['domain'], d['token'] # return domain and token
        

def authorize(domain, token):
    db_domain, db_token = get_domain(domain)

    # check if token matches
    if not db_domain or token != db_token:
        return False
    else:
        # return success
        return True


################    File system    ################

def delete_domain(domain):
    domain_dir = DOMAINS_DIRECTORY + "/" + domain + "/"

    # delete directory
    shutil.rmtree(domain_dir, ignore_errors=True)

    # delete nginx vhost
    # TODO

    return True

def deploy_package(domain, file):
    # save zip
    file.save(os.path.join(UPLOAD_DIRECTORY, domain + ".zip"))

    # clear and create directory
    domain_dir = DOMAINS_DIRECTORY + "/" + domain + "/"

    shutil.rmtree(domain_dir, ignore_errors=True)
    os.makedirs(domain_dir, exist_ok=True)

    # unzip package in domain directory
    try:
        with ZipFile(UPLOAD_DIRECTORY + '/' + domain + '.zip', 'r') as zip_obj:
            zip_obj.extractall(domain_dir)
        os.remove(UPLOAD_DIRECTORY + '/' + domain + '.zip') # remove zip
    except:
        return False, "Unzip domain package error"

    return True, "success"




################################    ROUTING    ################################


@app.route('/init', methods=['POST'])
def init():
    # get data from form
    try:
        new_domain = request.form['domain']
    except:
        response_data = { "status": "Client error" }
        return jsonify(response_data), 400 # Bad Request

    # check if domain exists
    db_domain, db_token = get_domain(new_domain)

    if db_domain:
        # domain exists, you can't create the same
        response_data = { "status": "Domain exists" }
        return jsonify(response_data), 400
    else:
        # domain not exists, you can create it
        token = secrets.token_hex(16)

        # add new domain to db
        db.insert( { "domain": new_domain, "token": token } )

        response_data = { "status": "Success", "token": token }
        return jsonify(response_data), 200


@app.route('/delete', methods=['POST'])
def delete():
    # get form
    try:
        token = request.form['token']
        domain = request.form['domain']
    except:
        response_data = { "status": "Client error" }
        return jsonify(response_data), 400 # Bad Request

    # authorization
    if not authorize(domain, token):
        response_data = { "status": "Unauthorized"}
        return jsonify(response_data), 401
    else:
        # delete directory and configurations
        delete_domain(domain)

        # delete domain from db
        db_domain, db_token = get_domain(domain)
        if db_domain:
            db.remove(where('domain') == db_domain)

            # return successful response
            response_data = { "status": "Success" }
            return jsonify(response_data), 200
        else:
            # error
            response_data = { "status": "Domain not found" }
            return jsonify(response_data), 404


@app.route('/deploy', methods=['POST'])
def deploy():
    # get form
    try:
        token = request.form['token']
        domain = request.form['domain']
        file = request.files['file']
    except:
        response_data = { "status": "Client error" }
        return jsonify(response_data), 400 # Bad Request

    # authorization
    if not authorize(domain, token):
        response_data = { "status": "Unauthorized"}
        return jsonify(response_data), 401
    else:
        status, status_text = deploy_package(domain, file)
        if not status:
            response_data = { "status": status_text }
            return jsonify(response_data), 500

        # reload nginx TODO

        response_data = { "status": status_text }
        return jsonify(response_data), 200


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True) # start aplikacji, polaczenie do lokalnego hosta, wlaczenie pokazywania bledow
