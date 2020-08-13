import json
import uuid

from PsqlHelper import PsqlHelper


class Helper:
    ph = PsqlHelper()

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
        return json.dumps({"registration": "ok",
                           "request_id": request_id})

    def get_user_requests(self, user_id, limit):
        if not limit:
            limit = 25
        records_active = []
        records_closed = []
        records_new, columns = self.ph.get_requests(user_id, limit, ['new', 'in progress'])
        records_old, columns = self.ph.get_requests(user_id, limit, ['closed'])
        for record in records_new:
            request_data_dict = {}
            for i in range(len(columns) - 1):
                request_data_dict.update({columns[i]: record[i]})
            request_data_dict.update({"date": record[len(columns) - 1].strftime('%Y-%m-%d')})
            records_active.append(request_data_dict)
        for record in records_old:
            request_data_dict = {}
            for i in range(len(columns) - 1):
                request_data_dict.update({columns[i]: record[i]})
            request_data_dict.update({"date": record[len(columns) - 1].strftime('%Y-%m-%d')})
            records_closed.append(request_data_dict)
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

    def job_registration(self, job_dict):
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
                                    cost_price, request_id, description)
        return json.dumps({"jobs": {"job_id": job_id}})
