from flask import Flask, request

from Helper import Helper
from PsqlHelper import PsqlHelper

app = Flask(__name__)
ph = PsqlHelper()
h = Helper()


@app.route('/')
def index():
    return 'Welcome to certification services main page!'


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


@app.route('/requests/updateStatus', methods=['PUT'])
def update_request_status():
    request_dict = request.get_json()
    return h.update_request_status(request_dict)


@app.route('/requests/getByUserId', methods=['GET'])
def get_user_requests():
    user_id = request.args.get('userId')
    limit = request.args.get('limit')
    return h.get_user_requests(user_id, limit)


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


@app.route('/tokens/notification/post', methods=['PUT'])
def update_token():
    token_dict = request.get_json()
    return h.update_token(token_dict)


if __name__ == "__main__":
    # app.run(host='0.0.0.0')
    app.run()
