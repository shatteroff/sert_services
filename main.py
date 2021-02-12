import json
from functools import wraps

import jwt
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from Helper import Helper
from PsqlHelper import PsqlHelper

try:
    from Config import Config
except:
    from Config_local import Config

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = Config.SECRET_KEY
ph = PsqlHelper()
h = Helper()
auth_header_str = 'Authorization'
custom_headers = {'Access-Control-Allow-Origin': '*',
                  'Access-Control-Allow-Credentials': 'true',
                  'Access-Control-Allow-Methods': 'DELETE, POST, GET, PUT, OPTIONS',
                  'Access-Control-Allow-Headers':
                      'Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With, Access-Control-Max-Age, ACCESS-TOKEN'}


@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description
    })
    response.content_type = "application/json"
    return response


def check_for_token(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        token = request.headers.get(auth_header_str)
        if not token:
            return jsonify({'Authorization error': 'Missing token'}), 403
        try:
            token_data = jwt.decode(token, app.config['SECRET_KEY'])
            # user_id = token_data.get('user_id')
            # if role:
            #     role = role.lower()
            # start_time = time.time()
            data = func(token_data)
            # print('Execution time ', int((time.time() - start_time) * 1000))
            return data
        except jwt.exceptions.PyJWTError:
            return jsonify({'Authorization error': 'Invalid token'}), 403

    return wrapped


@app.route('/')
def index():
    return 'Welcome to certification services main page!'


@app.route('/login/post', methods=['POST'])
def login():
    login_dict = request.get_json()
    user_login = login_dict.get('login')
    password = login_dict.get('password')
    firebase_token = login_dict.get('firebase_token')
    token = h.user_login(user_login, password, firebase_token, app.config['SECRET_KEY'])
    return token


@app.route('/registration', methods=['POST'])
def registration():
    user_dict = request.get_json()
    return h.user_registration(user_dict)


@app.route('/users/addInfo', methods=['POST'])
@check_for_token
def add_user_info(token_data):
    auth_user_id = token_data.get('user_id')
    user_dict = request.get_json()
    user_dict.update({'user_id': auth_user_id})
    return h.add_user_info(user_dict)


@app.route('/users/getUserInfoById', methods=['GET'])
@check_for_token
def get_user_info(token_data):
    user_id = request.args.get('id')
    role = token_data.get('role')
    if role == 'admin':
        return h.get_user_info(user_id)
    else:
        return jsonify({"Access_error": "Insufficient rights to use the resource"}), 403


@app.route('/users/getTemplatesPath', methods=['GET'])
@check_for_token
def get_user_info(token_data):
    user_id = token_data.get('user_id')
    return h.get_docs_template_path(user_id)


@app.route('/requests/post', methods=['POST'])
@check_for_token
def post_request(token_data):
    request_dict = request.get_json()
    auth_user_id = token_data.get('user_id')
    request_dict.update({'user_id': auth_user_id})
    request_dict.update({'user_name': token_data.get('user_name')})
    return h.request_registration(request_dict)


@app.route('/requests/updateInfo', methods=['POST'])
@check_for_token
def update_request(token_data):
    request_dict = request.get_json()
    auth_user_id = token_data.get('user_id')
    request_dict.update({'user_id': auth_user_id})
    request_dict.update({'user_name': token_data.get('user_name')})
    return h.request_update(request_dict)


@app.route('/requests/updateStatus', methods=['PUT', 'POST'])
@check_for_token
def update_request_status(token_data):
    # if role == 'admin':
    request_dict = request.get_json()
    return h.update_request_status(request_dict)
    # else:
    #     return jsonify({"Access error": "Insufficient rights to use the resource"}), 403


@app.route('/requests/getByUserId', methods=['GET'])
@check_for_token
def get_user_requests(token_data):
    # token = request.headers.get(auth_header_str)
    # token_data = h.check_token(token, app.config['SECRET_KEY'])
    # if token_data:
    limit = request.args.get('limit')
    #     user_id = token_data.get('user_id')
    from_dt = request.args.get('from')
    auth_user_id = token_data.get('user_id')
    role = token_data.get('role')
    if role:
        role = role.lower()
    if role == 'admin':
        user_id = request.args.get('userId')
        return h.get_user_requests(limit, user_id=user_id, from_dt=from_dt)
    elif role == 'expert':
        return h.get_user_requests(limit, expert_id=auth_user_id, from_dt=from_dt)
    else:
        return h.get_user_requests(limit, user_id=auth_user_id, from_dt=from_dt)


@app.route('/requests/getInfo', methods=['GET'])
@check_for_token
def get_request_info(token_data):
    request_id = request.args.get('id')
    auth_user_id = token_data.get('user_id')
    return h.get_request_info(request_id, auth_user_id)


@app.route('/requests/addRequiredInfo', methods=['POST'])
@check_for_token
def add_request_info(*args):
    info_dict = request.get_json()
    return h.add_request_info(info_dict)


@app.route('/requests/addFiles', methods=['POST'])
@check_for_token
def add_files_to_request(token_data):
    info_dict = request.get_json()
    info_dict.update({'user_id': token_data.get('user_id')})
    return h.add_files_to_request(info_dict)


@app.route('/jobs/post', methods=['POST'])
@check_for_token
def post_job(token_data):
    auth_user_id = token_data.get('user_id')
    job_dict = request.get_json()
    role = token_data.get('role')
    if role:
        role = role.lower()
    if role != 'admin':
        job_dict.update({'user_id': auth_user_id})
    return h.job_registration(job_dict)


@app.route('/jobs/getByUserId', methods=['GET'])
@check_for_token
def get_user_jobs(token_data):
    # user_id = request.args.get('userId')
    auth_user_id = token_data.get('user_id')
    role = token_data.get('role')
    if role:
        role = role.lower()
    limit = request.args.get('limit')
    # return h.get_jobs(limit, user_id=user_id)
    if role == 'admin':
        user_id = request.args.get('userId')
        return h.get_jobs(limit, user_id=user_id)
    else:
        return h.get_jobs(limit, user_id=auth_user_id)


@app.route('/promos/checkCodeForExist', methods=['GET'])
def check_promo_code():
    return h.get_promo_code(request.args.get('code'))


@app.route('/leaderboard/getLeaders', methods=['GET'])
@check_for_token
def get_leaderboard(*args):
    limit = request.args.get('limit')
    return h.get_leader_board(limit)


@app.route('/tokens/notification/post', methods=['POST'])
@check_for_token
def set_token(token_data):
    auth_user_id = token_data.get('user_id')
    token_dict = request.get_json()
    token_dict.update({'user_id': auth_user_id})
    return h.set_token(token_dict)


@app.route('/users/getPaymentStatement', methods=['GET'])
def get_payment_statement():
    file = h.get_payment_statement(.65, .7)
    return Response(file.encode('utf-8-sig'), mimetype="text/plain",
                    headers={"Content-Disposition": "attachment;filename=payments.csv"})


@app.route('/getId', methods=['GET'])
@check_for_token
def get_id(*args):
    id_type = request.args.get('type')
    if id_type:
        return h.get_id(id_type)


@app.route('/auth/<login>/<password>', methods=['GET'])
def auth(login, password):
    return ph.get_login(login, password)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
    # app.run(host='0.0.0.0',port=8000)
