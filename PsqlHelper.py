import json
import uuid

import psycopg2


class PsqlHelper():

    @staticmethod
    def execute_query(query, commit=False):
        records = ''
        conn = psycopg2.connect(dbname='dbojgd8kb7avuc', user='jpsarrqiurvslr',
                                password='9a473bf4a600d9abb06e8550c0e1aaa23fb7b09762113bcb8c6504e504d3e93e',
                                host='ec2-34-239-241-25.compute-1.amazonaws.com')
        cursor = conn.cursor()
        cursor.execute(query)
        if not commit:
            records = cursor.fetchall()
        cursor.close()
        conn.commit()
        conn.close()
        return records

    def get_login(self, login, password):
        query = 'Select * from public.users'
        try:
            login = int(login)
            query += f' where phone = {login}'
        except ValueError:
            query += f" where email = '{login}'"
        query += f" and password = '{password}'"
        records = self.execute_query(query)
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
            records = self.execute_query(query_phone)
            if records:
                error_list.append('phone')
        if email:
            query_email = query + f" where email = '{email}'"
            records = self.execute_query(query_email)
            if records:
                error_list.append('email')
        if alias:
            query_alias = query + f" where alias = '{alias}'"
            records = self.execute_query(query_alias)
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
        self.execute_query(query, commit=True)

    def get_all_ids(self, id_type):
        ids = []
        query = f'select id from public.{id_type}'
        records = self.execute_query(query)
        for record in records:
            ids.append(record[0])
        return ids
