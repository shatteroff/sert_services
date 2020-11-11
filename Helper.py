import json
import uuid

import jwt

from FirebaseHelper import FirebaseHelper
from PsqlHelper import PsqlHelper

try:
    from Config import Config
except:
    from Config_local import Config


class Helper:
    ph = PsqlHelper()
    fbh = FirebaseHelper()

    @staticmethod
    def get_token(payload, secret_key):
        token = jwt.encode(
            payload,
            secret_key)
        return token

    # def user_login(self, login, password, firebase_token, secret_key):
    #     payload = {}
    #     user_info = self.ph.get_user_info(login, password)
    #     if user_info == 1:
    #         return json.dumps({"Login error": "Error"}), 401
    #     elif user_info == 0:
    #         return json.dumps({"Login error": "Non-existent user"}), 401
    #     else:
    #         user_id = user_info[0]
    #         payload.update({'user_id': user_id})
    #         payload.update({'yandex_token': Config.YANDEX_TOKEN})
    #         request_id = user_info[2]
    #         job_id = user_info[3]
    #         if firebase_token:
    #             self.ph.insert_notification_token(user_id, firebase_token)
    #         if user_info[1]:
    #             payload.update({'role': user_info[1]})
    #         # request_id = self.ph.get_empty_request_id(user_id)
    #         if not request_id:
    #             request_id = self.ph.registration_request(user_id)
    #         payload.update({'request_id': request_id})
    #         # job_id = self.ph.get_empty_job_id(user_id)
    #         if not job_id:
    #             job_id = self.ph.registration_job(user_id)
    #         payload.update({'job_id': job_id})
    #         return json.dumps(({'token': self.get_token(payload, secret_key).decode('utf-8')}))

    def user_login(self, login, password, firebase_token, secret_key):
        payload = {'yandex_token': Config.YANDEX_TOKEN}
        user_info = self.ph.get_user_id(login, password)
        if user_info == 1:
            return json.dumps({"Login error": "Error"}), 401
        elif user_info == 0:
            return json.dumps({"Login error": "Non-existent user"}), 401
        else:
            user_id = user_info[0]
            payload.update({'user_id': user_id})
            user_name = user_info[2]
            payload.update({'user_name': user_name})
            email = user_info[4]
            if not email:
                email = user_info[3]
            payload.update({'contact': email})
            if firebase_token:
                self.ph.insert_notification_token(user_id, firebase_token)
            if user_info[1]:
                payload.update({'role': user_info[1]})
            return json.dumps(({'token': self.get_token(payload, secret_key).decode('utf-8')}))

    def user_registration(self, user_dict):
        phone = user_dict.get('phone')
        if phone:
            try:
                phone = int(phone)
                if len(str(phone)) != 10:
                    return json.dumps({"registration": {"error": "wrong phone format"}}), 500
            except ValueError:
                return json.dumps({"registration": {"error": 'value for "phone" must be integer'}}), 500
        email = user_dict.get('email')
        alias = user_dict.get('alias')
        name = user_dict.get('name')
        password = user_dict.get('password')
        error_list = self.ph.get_exist_users(phone, email, alias)
        if error_list:
            # errors = ','.join(f'"{x}"' for x in error_list)
            json_ex = json.dumps({"registration": {"errors": error_list}})
            print(json_ex)
            return json_ex
        else:
            if alias and password and (phone or email):
                self.ph.insert_user(phone, email, alias, name, password)
                return json.dumps({"registration": "ok"})
            else:
                return json.dumps({"registration": {"error": "please, fill in all required fields"}}), 500

    def get_id(self, id_type):
        ids = self.ph.get_all_ids(id_type)
        id_new = uuid.uuid4()
        while id_new in ids:
            id_new = uuid.uuid4()
        return json.dumps({"id": str(id_new)})

    def request_registration(self, request_dict):
        user_id = request_dict.get('user_id')
        request_id = request_dict.get('request_id')
        request_type = request_dict.get('request_type')
        custom_code = request_dict.get('custom_code')
        product_type = request_dict.get('product_type')
        doc_type = request_dict.get('doc_type')
        validity_period = request_dict.get('validity_period')
        add_info = request_dict.get('add_info')
        files = request_dict.get('files')
        self.ph.insert_request(user_id, request_type, custom_code, product_type, doc_type, validity_period, add_info,
                               request_id,files)
        # request_new_id = self.ph.registration_request(user_id)
        return json.dumps({"request_registration": "ok"})
                              # , "request_id": request_new_id})

    # def get_user_requests(self, limit, user_id=None):
    #     if not limit:
    #         limit = 25
    #     records_active = []
    #     records_closed = []
    #     records_new, columns = self.ph.get_requests(limit, [0, 1, 2], user_id=user_id)
    #     records_old, columns = self.ph.get_requests(limit, [999], user_id=user_id)
    #     for record in records_new:
    #         request_data_dict = {}
    #         for i in range(len(columns) - 1):
    #             request_data_dict.update({columns[i]: record[i]})
    #         # request_data_dict.update({"date": record[len(columns) - 1].strftime('%d.%m.%Y %H:%M:%S')})
    #         request_data_dict.update({"date": record[len(columns) - 1].isoformat()})
    #         records_active.append(request_data_dict.copy())
    #     for record in records_old:
    #         request_data_dict = {}
    #         for i in range(len(columns) - 1):
    #             request_data_dict.update({columns[i]: record[i]})
    #         # request_data_dict.update({"date": record[len(columns) - 1].strftime('%d.%m.%Y %H:%M:%S')})
    #         request_data_dict.update({"date": record[len(columns) - 1].isoformat()})
    #         records_closed.append(request_data_dict.copy())
    #     requests_dict = {}
    #     if records_active:
    #         active_dict = {"active": records_active}
    #         print(len(records_active))
    #         requests_dict.update(active_dict)
    #     if records_closed:
    #         closed_dict = {"closed": records_closed}
    #         print(len(records_closed))
    #         requests_dict.update(closed_dict)
    #     if requests_dict:
    #         json_to_send = {"requests": requests_dict}
    #     else:
    #         json_to_send = {"requests": "empty"}
    #     return json.dumps(json_to_send, ensure_ascii=False)

    def get_user_requests(self, limit, user_id=None):
        if not limit:
            if user_id:
                limit = 25
        requests = []
        records, columns = self.ph.get_requests(limit, user_id=user_id)
        for record in records:
            request_data_dict = {}
            for i in range(len(columns)):
                request_data_dict.update({columns[i]: record[i]})
            # request_data_dict.update({"date": record[len(columns) - 1].strftime('%d.%m.%Y %H:%M:%S')})
            request_data_dict.update({"date": request_data_dict.pop("insert_dt").isoformat(timespec="seconds")})
            requests.append(request_data_dict.copy())
        # if requests_dict:
        json_to_send = {"requests": requests}
        # else:
        #     json_to_send = {"requests": "empty"}
        return json.dumps(json_to_send, ensure_ascii=False)

    def update_request_status(self, request_dict):
        user_id = request_dict.get('user_id')
        request_id = request_dict.get('request_id')
        status = int(request_dict.get('status'))
        notification = bool(request_dict.get('notify'))
        self.ph.update_request_status(user_id, request_id, status)
        if notification:
            client_token = self.ph.get_notification_token(user_id)
            title = 'Статус Вашего запроса был изменен'
            # body = 'Зайдите в приложение, чтобы узнать подробности'
            message_id = self.fbh.send_notification(client_token, title, request_id)
        return json.dumps({"request_update": "ok"})

    def job_registration(self, job_dict):
        job_id = job_dict.get('job_id')
        user_id = job_dict.get('user_id')
        request_id = job_dict.get('request_id')
        c_agreement = job_dict.get('customer_agreement')
        a_agreement = job_dict.get('agent_agreement')
        acts = job_dict.get('acts')
        title = job_dict.get('title')
        description = job_dict.get('description')
        custom_code = job_dict.get('custom_code')
        client_price = job_dict.get('client_price')
        cost_price = job_dict.get('cost_price')
        job_id = self.ph.insert_job(user_id, c_agreement, a_agreement, acts, title, custom_code, client_price,
                                    cost_price, request_id, description,job_id)
        # job_new_id = self.ph.registration_job(user_id)
        return json.dumps({"job_registration": "ok"})
                              # , "job_id": job_new_id})

    def get_jobs(self, limit, user_id=None):
        if not limit:
            limit = 25
        records, columns = self.ph.get_jobs(limit, user_id=user_id)
        job_data_dict = {}
        job_list = []
        for record in records:
            for i in range(len(columns)):
                if not (columns[i] == 'user_id'):
                    job_data_dict.update({columns[i]: record[i]})
            # job_data_dict.update({"date": record[len(columns) - 1].strftime('%d.%m.%Y %H:%M:%S')})
            job_data_dict.update({"date": job_data_dict.pop("insert_dt").isoformat(timespec="seconds")})
            job_list.append(job_data_dict.copy())
        # if job_list:
        json_to_send = {"jobs": job_list}
        # else:
        #     json_to_send = {"jobs": "empty"}
        return json.dumps(json_to_send, ensure_ascii=False)

    def get_leader_board(self, limit):
        if not limit:
            limit = 20
        records, columns = self.ph.get_margins(limit)
        margin_list = []
        if records:
            for record in records:
                margin_list.append({key: value for key, value in zip(columns, record)})
            json_to_send = {"leaderboard": margin_list}
        else:
            json_to_send = {"leaderboard": "empty"}
        return json.dumps(json_to_send, ensure_ascii=False)

    def set_token(self, token_dict):
        user_id = token_dict.get('user_id')
        token = token_dict.get('firebase_token')
        self.ph.insert_notification_token(user_id, token)
        return json.dumps({"token_registration": "ok"})

    def update_token(self, token_dict):
        user_id = token_dict.get('user_id')
        token = token_dict.get('token')
        self.ph.update_notification_token(user_id, token)
        return json.dumps({"token_update": "ok"})
