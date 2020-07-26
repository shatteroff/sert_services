import json
import uuid

from PsqlHelper import PsqlHelper


class Helper():
    ph = PsqlHelper()

    def registration(self, user_dict):
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
