import json
import uuid

from FirebaseHelper import FirebaseHelper
from PsqlHelper import PsqlHelper


class Helper:
    ph = PsqlHelper()
    fbh = FirebaseHelper()

    def user_registration(self, user_dict):
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
                return 'Please, fill in required fields', 500

    def get_id(self, id_type):
        ids = self.ph.get_all_ids(id_type)
        id_new = uuid.uuid4()
        while id_new in ids:
            id_new = uuid.uuid4()
        return json.dumps({"id": str(id_new)})

    def request_registration(self, request_dict):
        user_id = request_dict.get('user_id')
        request_type = request_dict.get('request_type')
        custom_code = request_dict.get('custom_code')
        product_type = request_dict.get('product_type')
        doc_type = request_dict.get('doc_type')
        validity_period = request_dict.get('validity_period')
        add_info = request_dict.get('add_info')
        request_id = self.ph.insert_request(user_id, request_type, custom_code, product_type, doc_type, validity_period,
                                            add_info)
        return json.dumps({"request_registration": "ok",
                           "request_id": request_id})

    def get_user_requests(self, user_id, limit):
        if not limit:
            limit = 25
        records_active = []
        records_closed = []
        records_new, columns = self.ph.get_requests(user_id, limit, [0, 1, 2])
        records_old, columns = self.ph.get_requests(user_id, limit, [999])
        for record in records_new:
            request_data_dict = {}
            for i in range(len(columns) - 1):
                request_data_dict.update({columns[i]: record[i]})
            request_data_dict.update({"date": record[len(columns) - 1].strftime('%Y-%m-%d')})
            records_active.append(request_data_dict.copy())
        for record in records_old:
            request_data_dict = {}
            for i in range(len(columns) - 1):
                request_data_dict.update({columns[i]: record[i]})
            request_data_dict.update({"date": record[len(columns) - 1].strftime('%Y-%m-%d')})
            records_closed.append(request_data_dict.copy())
        requests_dict = {}
        if records_active:
            active_dict = {"active": records_active}
            requests_dict.update(active_dict)
        if records_closed:
            closed_dict = {"closed": records_closed}
            requests_dict.update(closed_dict)
        if requests_dict:
            json_to_send = {"requests": requests_dict}
        else:
            json_to_send = {"requests": "empty"}
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
            body = 'Зайдите в приложение, чтобы узнать подробности'
            message_id = self.fbh.send_notification(client_token, title, body)
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
                                    cost_price, request_id, description, job_id)
        return json.dumps({"job_registration": {"job_id": job_id}})

    def get_user_jobs(self, user_id, limit):
        if not limit:
            limit = 25
        records, columns = self.ph.get_jobs(user_id, limit)
        job_data_dict = {}
        job_list = []
        for record in records:
            for i in range(len(columns) - 1):
                if not (columns[i] == 'user_id'):
                    job_data_dict.update({columns[i]: record[i]})
            job_data_dict.update({"date": record[len(columns) - 1].strftime('%Y-%m-%d')})
            job_list.append(job_data_dict.copy())
        if job_list:
            json_to_send = {"jobs": job_list}
        else:
            json_to_send = {"jobs": "empty"}
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
        token = token_dict.get('token')
        self.ph.insert_notification_token(user_id, token)
        return json.dumps({"token_registration": "ok"})

    def update_token(self, token_dict):
        user_id = token_dict.get('user_id')
        token = token_dict.get('token')
        self.ph.update_notification_token(user_id, token)
        return json.dumps({"token_update": "ok"})
