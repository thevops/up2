import sys
import os
import requests
import json
    
from zipfile import ZipFile


################################    SETTINGS    ################################

CONFIG_FILE = ".up2.conf"
SCRIPT_NAME = None


################################    AUXILIARY    ################################


def logo():
    print('''
   ###################################
   #               ___          _    #
   #              |__ \        | |   #
   #    _   _ _ __   ) |  _ __ | |   #
   #   | | | | '_ \ / /  | '_ \| |   #
   #   | |_| | |_) / /_ _| |_) | |   #
   #    \__,_| .__/____(_) .__/|_|   #
   #         | |         | |         #
   #         |_|         |_|         #
   #                                 #
   ###################################
        ''')


def check_file_exists():
    if os.path.exists(CONFIG_FILE):
        return True
    else:
        return False

def read_config():
    try:
        with open(CONFIG_FILE) as json_file:
            data = json.load(json_file)
    except Exception as e:
        print("Read config file error", e)
        sys.exit(1)

    return data

def write_config(data):
    try:
        with open(CONFIG_FILE, 'w') as json_file:
            json.dump(data, json_file)
    except Exception as e:
        print("Write config file error", e)
        sys.exit(1)

    return True


def help(args):
    print('''
        This is up2 cli tool.

        Help:
            init     init your project
            deploy   deploy your project on platform
            delete   delete your project from platform

        use:
            {} [option]
        '''.format(args[0]))
    sys.exit(1)


def zip_current_directory(domain):
    with ZipFile(domain + '.zip', 'w') as zip_obj:
        for dirname, subdirname, filenames in os.walk("."): # current dir
            for f in filenames:
                if (f != CONFIG_FILE) and (f != SCRIPT_NAME):
                    filepath = os.path.join(dirname, f)
                    zip_obj.write(filepath)
    return str(domain + '.zip')


################################    MAIN functions    ################################


def init():
    # check if config file exists
    if os.path.exists(CONFIG_FILE):
        print("Config file exists. If you want to start new project, remove %s" % CONFIG_FILE)
        sys.exit(1)

    # get data from user
    server_url = input("Please, enter server application URL (http://127.0.0.1:5000): ")
    master_domain = input("Please, enter master domain name (up2.pl): ")
    domain = input("Please, enter domain that you want (testme): ")
    print("Your domain: %s" % (domain + "." + master_domain))
    print("Registration...")

    # request for domain
    try:
        r = requests.post(server_url + "/init", data={"domain": domain})
    except Exception as e:
        print("Init HTTP POST error", e)
        sys.exit(1)

    # check response
    if r.status_code == 200:
        try:
            response_json = r.json()
            # save token
            token = response_json['token']

            config_data = {"server_url": server_url, "master_domain": master_domain, "domain": domain, "token": token}
            write_config(config_data)

            print(response_json['status'])  
        except Exception as e:
            print("Parsing response error. Status", r.status_code, e)
            sys.exit(1)
    else:
        try:
            response_json = r.json()
            print("Reponse error.", response_json['status'])
        except Exception as e:
            print("Parse json error", e)
        



def deploy():
    print("Reading configs...")
    config_data = read_config()
    print("Ziping current directory...")
    zipfile = zip_current_directory(config_data['domain'])

    print("Sending package to server...")
    # send zip package to server
    files = {'file': open(zipfile,'rb')}
    data = {"domain": config_data['domain'], "token": config_data['token']}
    try:
        r = requests.post(config_data['server_url'] + "/deploy", data=data, files=files)
    except Exception as e:
        print("Deploy HTTP POST error", e)
        sys.exit(1)

    if r.status_code == 200:
        try:
            response_json = r.json()
            print(response_json['status'])
        except Exception as e:
            print("Parsing response error. Status", r.status_code, e)
            sys.exit(1)
    else:
        print("Reponse error. Status code", r.status_code)

    return True


def delete():
    print("Reading configs...")
    config_data = read_config()

    # send request
    try:
        r = requests.post(config_data['server_url'] + "/delete", data={"domain": config_data['domain'], "token": config_data['token']})
    except Exception as e:
        print("Delete HTTP POST error", e)
        sys.exit(1)

    if r.status_code == 200:
        try:
            response_json = r.json()
            print(response_json['status'])
        except Exception as e:
            print("Parsing response error. Status", r.status_code, e)
            sys.exit(1)

        # remove config file
        try:
            os.remove(CONFIG_FILE)
        except Exception as e:
            print("Remove config file error", e)
            sys.exit(1)
    else:
        print("Reponse error. Status code", r.status_code)

    return True



if __name__ == '__main__':
    logo()
    if len(sys.argv) <= 1:
        help(sys.argv)

    SCRIPT_NAME = sys.argv[0]
    # choose option
    if sys.argv[1] == "init":
        init()
    elif sys.argv[1] == "deploy":
        deploy()
    elif sys.argv[1] == "delete":
        delete()
    else:
        print("Invalid argument")
        help(sys.argv)

