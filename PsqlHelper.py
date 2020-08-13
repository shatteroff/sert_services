import json
import os
import uuid

import psycopg2


class PsqlHelper:

    @staticmethod
    def __execute_query(query, commit=False, is_return=False, is_columns_name=False):
        records = ''
        try:
            conn = psycopg2.connect(os.inviron['DATABASE'], sslmode='require')
            print('Connect via os')
        except AttributeError:
            conn = psycopg2.connect(dbname='dbojgd8kb7avuc', user='jpsarrqiurvslr',
                                    password='9a473bf4a600d9abb06e8550c0e1aaa23fb7b09762113bcb8c6504e504d3e93e',
                                    host='ec2-34-239-241-25.compute-1.amazonaws.com')
            print('Connect via full url')
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
        columns = ['user_id', 'status', 'request_type']
        values = [user_id, 'new', request_type]
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

    def insert_job(self, user_id, c_agreement, a_agreement, acts, title, custom_code, client_price, cost_price,
                   request_id=None, description=None):
        columns = ['user_id', 'customer_agreement', 'agent_agreement', 'acts', 'title', 'custom_code', 'client_price',
                   'cost_price']
        values = [user_id, c_agreement, a_agreement, acts, title, custom_code, client_price, cost_price]
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
