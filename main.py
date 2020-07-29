from flask import Flask, request

from Helper import Helper
from PsqlHelper import PsqlHelper

app = Flask(__name__)
ph = PsqlHelper()
h = Helper()


@app.route('/')
def index():
    return 'Hello World'


@app.route('/auth/<login>/<password>', methods=['GET'])
def auth(login, password):
    return ph.get_login(login, password)


@app.route('/registration', methods=['POST'])
def registration():
    user_dict = request.get_json()
    return h.user_registration(user_dict)


@app.route('/getId', methods=['GET'])
def get_id():
    id_type = request.args.get('type')
    if id_type:
        return h.get_id(id_type)


@app.route('/requests/post', methods=['POST'])
def post_request():
    request_dict = request.get_json()
    return h.request_registration(request_dict)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
    # app.run()
