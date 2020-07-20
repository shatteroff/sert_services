from flask import Flask, request
import json

from Helper import Helper
from PsqlHelper import PsqlHelper

app = Flask(__name__)
ph = PsqlHelper()
h = Helper()


@app.route('/')
def index():
    return 'Hello World'


@app.route('/auth/<login>/<password>')
def auth(login, password):
    return ph.get_login(login, password)


@app.route('/registration', methods=['POST'])
def registration():
    user_dict = request.get_json()
    return h.registration(user_dict)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
    # app.run()
