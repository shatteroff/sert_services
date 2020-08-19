import json

import psycopg2

from Config import Config


class PsqlHelper:

    @staticmethod
    def __execute_query(query, commit=False, is_return=False, is_columns_name=False):
        records = ''
        conn = psycopg2.connect(Config.psql_url, sslmode='require')
        cursor = conn.cursor()
        cursor.execute(query)
        if not commit or is_return:
            records = cursor.fetchall()
        if is_columns_name:
            columns = [desc[0] for desc in cursor.description]
        cursor.close()
        conn.commit()
        conn.close()
        if is_columns_name:
            return records, columns
        else:
            return records

    def get_login(self, login, password):
        query = 'Select * from public.users'
        try:
            login = int(login)
            query += f' where phone = {login}'
        except ValueError:
            query += f" where email = '{login}'"
        query += f" and password = '{password}'"
        records = self.__execute_query(query)
        if len(records) > 1:
            return json.dumps({"response": "Error"})
        elif len(records) == 0:
            return json.dumps({"response": "Empty data"})
        else:
            records = records[0]
            return json.dumps({"response": {"id": records[0], "alias": records[3], "name": records[4]}})

    def get_exist_users(self, phone, email, alias):
        error_list = []
        query = 'Select * from public.users'
        if phone:
            query_phone = query + f" where phone ='{phone}'"
            records = self.__execute_query(query_phone)
            if records:
                error_list.append('phone')
        if email:
            query_email = query + f" where email = '{email}'"
            records = self.__execute_query(query_email)
            if records:
                error_list.append('email')
        if alias:
            query_alias = query + f" where alias = '{alias}'"
            records = self.__execute_query(query_alias)
            if records:
                error_list.append('alias')
        return error_list

    def insert_user(self, phone, email, alias, name, password):
        if not phone:
            phone = 'null'
        if not email:
            email = 'null'
        else:
            email = f"'{email}'"
        if not name:
            name = 'null'
        else:
            name = f"'{name}'"

        query = f"INSERT INTO public.users(phone, email, alias, name, password)	" \
                f"VALUES ({phone},{email},'{alias}',{name},'{password}')"
        print(query)
        self.__execute_query(query, commit=True)

    def get_all_ids(self, id_type):
        ids = []
        query = f'select id from public.{id_type}'
        records = self.__execute_query(query)
        for record in records:
            ids.append(record[0])
        return ids

    def insert_request(self, user_id, request_type, custom_code=None, product_type=None, doc_type=None,
                       validity_period=None, add_info=None):
        columns = ['user_id', 'request_type']
        values = [user_id, request_type]
        if custom_code:
            columns.append('custom_code')
            values.append(custom_code)
        if product_type:
            columns.append('product_type')
            values.append(product_type)
        if doc_type:
            columns.append('doc_type')
            values.append(doc_type)
        if validity_period:
            columns.append('validity_period')
            values.append(validity_period)
        if add_info:
            columns.append('add_info')
            values.append(add_info)
        values = list(f"'{v}'" for v in values)
        query = f"INSERT INTO public.requests({','.join(columns)}) VALUES ({','.join(values)}) returning id"
        print(query)
        records = self.__execute_query(query, commit=True, is_return=True)
        return records[0][0]

    def get_requests(self, user_id, top_count, status_list):
        statuses = ','.join(f"'{status}'" for status in status_list)
        query = f"""select * from public.requests
                where user_id = '{user_id}' and status in ({statuses}) and request_type = 'app'
                order by insert_dt desc limit {top_count}"""
        records, columns = self.__execute_query(query, is_columns_name=True)
        return records, columns

    def update_request_status(self, user_id, request_id, status):
        query = f"""update public.requests set status = {status}
                where user_id='{user_id}' and id = '{request_id}'"""
        self.__execute_query(query, commit=True)

    def insert_job(self, user_id, c_agreement, a_agreement, acts, title, custom_code, client_price, cost_price,
                   request_id=None, description=None, job_id=None):
        columns = ['user_id', 'customer_agreement', 'agent_agreement', 'acts', 'title', 'custom_code', 'client_price',
                   'cost_price']
        values = [user_id, c_agreement, a_agreement, acts, title, custom_code, client_price, cost_price]
        if job_id:
            columns.append('id')
            values.append(job_id)
        if request_id:
            columns.append('request_id')
            values.append(request_id)
        if description:
            columns.append('description')
            values.append(description)
        values = list(f"'{v}'" for v in values)
        query = f"INSERT INTO public.projects({','.join(columns)}) VALUES ({','.join(values)}) returning id"
        print(query)
        records = self.__execute_query(query, commit=True, is_return=True)
        return records[0][0]

    def get_jobs(self, user_id, top_count):
        query = f"""select * from public.projects
                where user_id = '{user_id}'
                order by insert_dt desc limit {top_count}"""
        records, columns = self.__execute_query(query, is_columns_name=True)
        return records, columns

    def get_margins(self, top_count):
        query = f"""select m.*,u.name,u.alias from margin m
                join users u on m.user_id = u.id
                where margin>0
                order by margin desc limit {top_count}"""
        records, columns = self.__execute_query(query, is_columns_name=True)
        return records, columns

    def insert_notification_token(self, user_id, token):
        query = f"""insert into public.tokens (user_id,notification) VALUES ('{user_id}','{token}')"""
        self.__execute_query(query, commit=True)

    def update_notification_token(self, user_id, token):
        query = f"""update public.tokens set notification = '{token}', update_dt = CURRENT_TIMESTAMP
                where user_id = '{user_id}'"""
        self.__execute_query(query, commit=True)

    def get_notification_token(self, user_id):
        query = f"""select notification from public.tokens
                where user_id = '{user_id}'"""
        records = self.__execute_query(query)
        return records[0][0]
