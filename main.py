from flask import Flask, request
import json

from PsqlHelper import PsqlHelper

app = Flask(__name__)
ph = PsqlHelper()


@app.route('/')
def index():
    return 'Hello World'


@app.route('/auth/<login>/<password>')
def auth(login, password):
    return ph.get_login(login, password)


@app.route('/registration', methods=['POST'])
def registration():
    user_dict = request.get_json()
    phone = user_dict.get('phone')
    if phone:
        try:
            phone = int(phone)
            if len(str(phone)) != 10:
                return 'Wrong phone format', 500
        except ValueError:
            return 'Value for "phone" must be integer', 500
    email = user_dict.get('email')
    alias = user_dict.get('alias')
    name = user_dict.get('name')
    password = user_dict.get('password')
    error_list = ph.get_exist_users(phone, email, alias)
    if error_list:
        errors = ','.join(f'"{x}"' for x in error_list)
        json_ex = json.dumps(f'{{"registration":{{"errors":[{errors}]}}}}')
        print(json_ex)
        return json_ex
    else:
        if alias and password and (phone or email):
            ph.insert_user(phone, email, alias, name, password)
            return json.dumps('{"registration":"ok"}')
        else:
            return 'Please, fill in required fields', 500


if __name__ == "__main__":
    # app.run(host='0.0.0.0')
    app.run()
