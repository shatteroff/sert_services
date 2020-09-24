import time
from functools import wraps

import jwt
from flask import Flask, request, jsonify

from Config_local import Config
from Helper import Helper
from PsqlHelper import PsqlHelper

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
ph = PsqlHelper()
h = Helper()
auth_header_str = 'Authorization'


def check_for_token(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        token = request.headers.get(auth_header_str)
        if not token:
            return jsonify({'Authorization error': 'Missing token'}), 403
        try:
            token_data = jwt.decode(token, app.config['SECRET_KEY'])
            user_id = token_data.get('user_id')
            start_time = time.time()
            data = func(user_id)
            print('Execution time ', int((time.time() - start_time) * 1000))
            return data
        except jwt.exceptions.PyJWTError:
            return jsonify({'Authorization error': 'Invalid token'}), 403

    return wrapped


@app.route('/')
def index():
    return 'Welcome to certification services main page!'


@app.route('/auth/<login>/<password>', methods=['GET'])
def auth(login, password):
    return ph.get_login(login, password)


@app.route('/login', methods=['POST'])
def login():
    login_dict = request.get_json()
    user_login = login_dict.get('login')
    password = login_dict.get('password')
    token = h.user_login(user_login, password, app.config['SECRET_KEY'])
    return token


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


@app.route('/requests/updateStatus', methods=['PUT'])
def update_request_status():
    request_dict = request.get_json()
    return h.update_request_status(request_dict)


@app.route('/requests/getByUserId', methods=['GET'])
@check_for_token
def get_user_requests(user_id):
    # token = request.headers.get(auth_header_str)
    # token_data = h.check_token(token, app.config['SECRET_KEY'])
    # if token_data:
    limit = request.args.get('limit')
    #     user_id = token_data.get('user_id')
    if ph.get_user_role(user_id) == 'admin':
        return h.get_user_requests(limit)
    else:
        user_id = request.args.get('userId')
    return h.get_user_requests(limit, user_id=user_id)


# else:
#     return json.dumps({'Authorization error': 'wrong token'}), 403


@app.route('/jobs/post', methods=['POST'])
def post_job():
    job_dict = request.get_json()
    return h.job_registration(job_dict)


@app.route('/jobs/getByUserId', methods=['GET'])
def get_user_jobs():
    user_id = request.args.get('userId')
    limit = request.args.get('limit')
    return h.get_user_jobs(user_id, limit)


@app.route('/leaderboard/getLeaders', methods=['GET'])
def get_leaderboard():
    limit = request.args.get('limit')
    return h.get_leader_board(limit)


@app.route('/tokens/notification/post', methods=['POST'])
def set_token():
    token_dict = request.get_json()
    return h.set_token(token_dict)


if __name__ == "__main__":
    # app.run(host='0.0.0.0')
    app.run()
