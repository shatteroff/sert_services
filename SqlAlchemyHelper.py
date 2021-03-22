import json
import time
from datetime import datetime
from functools import wraps

import jwt
from sqlalchemy import or_, func
from sqlalchemy.orm import Query
from alchemy_encoder import AlchemyEncoder
from db_models import User, Request, PromoCode, AdditionalRequestInfo, Job, Leader, Margin, db

try:
    from Config import Config
except:
    from Config_local import Config


def exec_time(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        start_time = time.time()
        data = func(*args, **kwargs)
        # work_time = int((time.time() - start_time) * 1000)
        # print(f'Query execution time ', work_time, 'ms')
        return data

    return wrapped


class Helper:

    def __init__(self, app):
        self.db = db
        self.__session = db.session
        self.encoder = AlchemyEncoder()
        self.app = app

    def get_token(self, payload):
        token = jwt.encode(
            payload,
            self.app.config['SECRET_KEY'])
        return token

    @exec_time
    def user_registration(self, user_dict):
        errors = []
        email = user_dict.get('email')
        alias = user_dict.get('alias')
        query = self.__session.query(User)
        if user_dict.get('phone'):
            phone = int(user_dict.get('phone'))
            query = query.filter(or_(User.phone == phone, func.lower(User.email) == func.lower(email),
                                     func.lower(User.alias) == func.lower(alias)))
        else:
            query = query.filter(
                or_(func.lower(User.email) == func.lower(email), func.lower(User.alias) == func.lower(alias)))
        users = query.all()
        if users:
            for user in users:
                if user_dict.get('phone'):
                    if user.phone == phone:
                        errors.append('phone')
                if user.email.lower() == email.lower():
                    errors.append('email')
                if user.alias.lower() == alias.lower():
                    errors.append('alias')
        else:
            user = User(**user_dict)
            self.__session.add(user)
            self.__session.commit()
        return json.dumps({"registration": "ok" if not errors else {"errors": list(set(errors))}})

    @exec_time
    def user_login(self, user_dict):
        login = user_dict.pop("login")
        try:
            login = int(login)
            user_dict.update({"phone": login})
        except ValueError:
            user_dict.update({"email": login})
        user = self.__session.query(User).filter_by(**user_dict).one_or_none()
        if user:
            contact = user.email
            payload = {"user_id": user.id, "user_name": user.alias, "contact": contact,
                       "yandex_token": Config.YANDEX_TOKEN}
            if user.role_:
                role = user.role_.role
                payload.update({"role": role})
            return json.dumps(({'token': self.get_token(payload).decode('utf-8')}))
        else:
            return json.dumps({"Login error": "Non-existent user"}), 401

    @exec_time
    def update_user_info(self, user_dict):
        user_id = user_dict.pop('user_id')
        self.__session.query(User).filter_by(id=user_id).update(user_dict, synchronize_session=False)
        self.__session.commit()
        return json.dumps({"user_update": "ok"})

    @exec_time
    def get_user_info(self, user_id):
        user = self.__session.query(User).filter_by(id=user_id).one()
        user_dict = self.encoder.default(user)
        keys = ['password']
        for key in keys:
            user_dict.pop(key)
        if user.promo_.expert_user_:
            user_dict.update({"expert_name": user.promo_.expert_user_.name})
        user_dict.update(
            {"organization_name": user.promo_.organization_.name, "registered": user_dict.pop("insert_dt")})
        return json.dumps(user_dict, ensure_ascii=False)

    @exec_time
    def get_docs_template_path(self, user_id):
        user = self.__session.query(User).filter_by(id=user_id).one()
        return json.dumps({"templates_path": user.promo_.organization_.docs_path}, ensure_ascii=False)

    @exec_time
    def request_registration(self, request_dict):
        name = request_dict.pop('user_name')
        request_dict.update({"short_id": name[:3] + str(int(time.time())),
                             "id": request_dict.pop('request_id')})
        request = Request(**request_dict)
        self.__session.add(request)
        self.__session.commit()
        return json.dumps({"request_registration": "ok"})

    @exec_time
    def request_update(self, request_dict):
        filter_dict = {}
        filter_keys = ['request_id', 'user_id']
        for key in filter_keys:
            if key == filter_keys[0]:
                filter_dict.update({'id': request_dict.pop(key)})
            else:
                filter_dict.update({key: request_dict.pop(key)})
        res = self.__session.query(Request).filter_by(**filter_dict).update(request_dict, synchronize_session=False)
        self.__session.commit()
        return json.dumps({"request_update": "ok"})

    @exec_time
    def get_requests(self, user_id=None, auth_user_id=None, role=None, from_dt=None, limit=None):
        if not limit:
            limit = 25
        query = self.__session.query(Request).join(User).filter_by(id=auth_user_id)
        if role == 'expert':
            query = self.__session.query(Request).join(User).join(PromoCode,
                                                                  User.promo_code == PromoCode.code).filter_by(
                expert_id=auth_user_id)
        elif role == 'admin':
            query = self.__session.query(Request)
        if from_dt:
            query = query.filter(Request.update_dt > from_dt)
        query = query.order_by(Request.date.desc()).limit(limit)
        requests = self.__session.query(Request).from_statement(query).all()
        requests_list = json.loads(json.dumps(requests, cls=AlchemyEncoder))
        requests_dict = {"requests": requests_list, "time": datetime.utcnow().isoformat(timespec="seconds")}
        return json.dumps(requests_dict, ensure_ascii=False)

    @exec_time
    def add_files_to_request(self, request_dict):
        files = request_dict.pop("files")
        request_dict.update({"id": request_dict.pop("request_id")})
        request = self.__session.query(Request).filter_by(**request_dict).one()
        files += request.files
        request.files = list(set(files))
        self.__session.commit()
        return json.dumps({"files_upload": "ok"})

    @exec_time
    def add_request_info(self, request_dict):
        add_info = AdditionalRequestInfo(**request_dict)
        filter_dict = {}
        filter_keys = ['request_id', 'user_id']
        for key in filter_keys:
            filter_dict.update({key: request_dict.pop(key)})
        result = self.__session.query(AdditionalRequestInfo).filter_by(**filter_dict).first()
        if result:
            self.__session.query(AdditionalRequestInfo).filter_by(**filter_dict).update(request_dict,
                                                                                        synchronize_session=False)
        else:
            self.__session.add(add_info)
        self.__session.commit()
        return json.dumps({"update_request_info": "ok"})

    @exec_time
    def get_request_info(self, filter_dict):
        request_info = self.__session.query(AdditionalRequestInfo).filter_by(**filter_dict).one_or_none()
        return json.dumps(request_info if request_info else {}, cls=AlchemyEncoder, ensure_ascii=False)

    @exec_time
    def job_registration(self, job_dict):
        job_dict.update({"id": job_dict.pop('job_id')})
        job = Job(**job_dict)
        self.__session.add(job)
        self.__session.commit()
        return json.dumps({"job_registration": "ok"})

    @exec_time
    def job_update(self, job_dict):
        filter_dict = {}
        filter_keys = ['job_id', 'user_id']
        for key in filter_keys:
            if key == filter_keys[0]:
                filter_dict.update({'id': job_dict.pop(key)})
            else:
                filter_dict.update({key: job_dict.pop(key)})
        self.__session.query(Job).filter_by(**filter_dict).update(job_dict, synchronize_session=False)
        self.__session.commit()
        return json.dumps({"job_update": "ok"})

    @exec_time
    def get_jobs(self, user_id=None, auth_user_id=None, role=None, limit=None):
        if not limit:
            limit = 25
        query = Query(Job).join(User).filter_by(id=auth_user_id)
        if role == 'expert':
            query = Query(Job).join(User).join(PromoCode, User.promo_code == PromoCode.code).filter_by(
                expert_id=auth_user_id)
        elif role == 'admin':
            query = Query(Job)
        # if from_dt:
        #     query = query.filter(Job.date > from_dt)
        query = query.order_by(Job.date.desc()).limit(limit)
        jobs = self.__session.query(Job).from_statement(query).all()
        return json.dumps({"jobs": jobs}, cls=AlchemyEncoder, ensure_ascii=False)

    @exec_time
    def check_promo_code_for_exists(self, promo_code):
        result = self.__session.query(PromoCode).filter_by(code=promo_code).first()
        return json.dumps({"promo": "ok" if result else "wrong promo_code"})

    @exec_time
    def get_leaderboard(self, limit=None):
        if not limit:
            limit = 15
        leaders = self.__session.query(Leader).join(User).filter(Leader.margin > 0,
                                                                 User.is_in_leaderboard == True).order_by(
            Leader.full_price.desc()).limit(limit).all()
        return json.dumps({"leaderboard": leaders}, cls=AlchemyEncoder, ensure_ascii=False)

    @exec_time
    def get_margins(self, limit):
        if not limit:
            limit = 15
        leaders = self.__session.query(Margin).filter(Margin.margin > 0).order_by(Margin.full_price.desc()).limit(
            limit).all()
        return json.dumps({"leaderboard": leaders}, cls=AlchemyEncoder, ensure_ascii=False)
