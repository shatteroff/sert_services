import json
from functools import wraps

import jwt
from flask import Flask, request, jsonify
from flask_cors import CORS
# from flask_mail import Mail, Message
from werkzeug.exceptions import HTTPException

from SqlAlchemyHelper import Helper

try:
    from Config import Config
except:
    from Config_local import Config

app = Flask(__name__)
app.config.update(
    SECRET_KEY=Config.SECRET_KEY,
    SQLALCHEMY_DATABASE_URI=Config.psql_url,
    MAIL_SERVER='smtp.mail.ru',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    # MAIL_USERNAME=Config.MAIL_USERNAME,
    # MAIL_DEFAULT_SENDER=Config.MAIL_USERNAME,
    # MAIL_PASSWORD=Config.MAIL_PASSWORD
)
CORS(app)
# mail = Mail(app)
h = Helper(app)
h.db.init_app(app)
auth_header_str = 'Authorization'


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
            data = func(token_data)
            print(f"Token data: {json.dumps(token_data, ensure_ascii=False)}")
            # print('Execution time ', int((time.time() - start_time) * 1000))
            return data
        except jwt.exceptions.PyJWTError:
            return jsonify({'Authorization error': 'Invalid token'}), 403

    return wrapped


@app.after_request
def print_incoming_message(data):
    incoming_data = f"{request.data.decode('utf-8')}"
    if not incoming_data:
        incoming_data = 'Empty data'
    print(f"Incoming data: {incoming_data}")
    return data


@app.route('/')
def index():
    return 'Welcome to certification plus api main page!'


@app.route('/login/post', methods=['POST'])
def login():
    login_dict = request.get_json()
    if login_dict.get("firebase_token"):
        login_dict.pop("firebase_token")
    token = h.user_login(login_dict)
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
    return h.update_user_info(user_dict)


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
def get_user_templates_path(token_data):
    user_id = token_data.get('user_id')
    return h.get_docs_template_path(user_id)


@app.route('/users/getStatistic', methods=['GET'])
@check_for_token
def get_user_statistic(token_data):
    # user_id = request.args.get('user_id')
    user_id = token_data.get('user_id')
    return h.get_statistic(user_id)


@app.route('/payments', methods=['POST'])
@check_for_token
def post_payment(token_data):
    return h.add_payments(request.get_json())


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
    # auth_user_id = token_data.get('user_id')
    # request_dict.update({'user_id': auth_user_id})
    # request_dict.update({'user_name': token_data.get('user_name')})
    return h.request_update(request_dict)


@app.route('/requests/updateStatus', methods=['PUT', 'POST'])
@check_for_token
def update_request_status(token_data):
    request_dict = request.get_json()
    if request_dict.get('user_id') is None:
        request_dict.update({'user_id': token_data.get('user_id')})
    return h.request_update(request_dict)


@app.route('/requests/getByUserId', methods=['GET'])
@check_for_token
def get_user_requests(token_data):
    user_id = request.args.get('userId')
    limit = request.args.get('limit')
    from_dt = request.args.get('from')

    auth_user_id = token_data.get('user_id')
    role = token_data.get('role')
    if role:
        role = role.lower()
    return h.get_requests(user_id, auth_user_id, role, from_dt, limit)


@app.route('/requests/getInfo', methods=['GET'])
@check_for_token
def get_request_info(token_data):
    filter_dict = dict(request.args)
    role = token_data.get('role')
    if role:
        if role.lower() == 'admin':
            user_id = request.args.get('user_id')
            if user_id:
                filter_dict.update({'user_id': user_id})
    return h.get_request_info(filter_dict)


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


@app.route('/requests/getStatuses', methods=['GET'])
@check_for_token
def get_statuses(token_data):
    return h.get_request_statuses()


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
    user_id = request.args.get('userId')
    limit = request.args.get('limit')

    auth_user_id = token_data.get('user_id')
    role = token_data.get('role')
    if role:
        role = role.lower()
    return h.get_jobs(user_id, auth_user_id, role, limit)


@app.route('/promos/checkCodeForExist', methods=['GET'])
def check_promo_code():
    return h.check_promo_code_for_exists(request.args.get('code'))


@app.route('/leaderboard/getLeaders', methods=['GET'])
@check_for_token
def get_leaderboard(*args):
    limit = request.args.get('limit')
    # return h.get_margins(limit)
    return h.get_leaderboard(limit)


# @app.route('/users/getPaymentStatement', methods=['GET'])
# def get_payment_statement():
#     file = h.get_payment_statement(.65, .7)
#     return Response(file.encode('utf-8-sig'), mimetype="text/plain",
#                     headers={"Content-Disposition": "attachment;filename=payments.csv"})


# @app.route('/email/test')
# def send_mail():
#     msg = Message("Feedback", recipients=['zapros@certificate-plus.ru'])
#     msg.body = "Привет котлета!"
#     mail.send(msg)
#     return "msg send"


if __name__ == "__main__":
    if Config.port:
        app.run(host='0.0.0.0', port=Config.port)
    else:
        app.run(host='0.0.0.0')
