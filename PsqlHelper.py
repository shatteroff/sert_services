import json

import psycopg2


class PsqlHelper():

    def execute_query(self, query, commit=False):
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
            return 'Error'
        elif len(records) == 0:
            return json.dumps({"response": "Empty data"})
        else:
            records = records[0]
            return json.dumps({"response": {"id": records[0], "alias": records[3], "name": records[4]}})

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
