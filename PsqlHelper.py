import json
from functools import wraps
import time
import psycopg2

try:
    from Config import Config
except:
    from Config_local import Config


def exec_time(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        start_time = time.time()
        data = func(*args, **kwargs)
        print(f'Query execution time ', int((time.time() - start_time) * 1000), 'ms')
        return data

    return wrapped


class PsqlHelper:
    empty_request_type = 'empty_type'

    @staticmethod
    @exec_time
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

    def get_user_id(self, login, password):
        query = f"""select u.id,r.role,u.name,u.phone,u.email from users u
                left join public.roles r on u.id=r.user_id
                """
        try:
            login = int(login)
            query += f' where phone = {login}'
        except ValueError:
            query += f" where email = '{login}'"
        query += f" and password = '{password}'"
        records = self.__execute_query(query)
        if len(records) > 1:
            return 1
        elif len(records) == 0:
            return 0
        else:
            user_info = records[0]
            return user_info

    # def get_user_info(self, login, password):
    #     query = f"""select u.id,r.role,req.id as request_id, pro.id as job_id from users u
    #             left join public.roles r on u.id=r.user_id
    #             left join requests req on req.user_id = u.id and req.request_type = '{self.empty_request_type}'
    #             left join projects pro on pro.user_id = u.id and pro.customer_agreement = '{self.empty_request_type}'
    #             and agent_agreement = '{self.empty_request_type}' and title = '{self.empty_request_type}'
    #             """
    #     try:
    #         login = int(login)
    #         query += f' where phone = {login}'
    #     except ValueError:
    #         query += f" where email = '{login}'"
    #     query += f" and password = '{password}'"
    #     records = self.__execute_query(query)
    #     if len(records) > 1:
    #         return 1
    #     elif len(records) == 0:
    #         return 0
    #     else:
    #         user_info = records[0]
    #         return user_info

    def update_user_info(self, user_id, workplace=None, account_number=None):
        columns = []
        values = []
        if workplace:
            columns.append('workplace')
            values.append(workplace)
        if account_number:
            columns.append('account_number')
            values.append(account_number)
        sets = (f"{column}='{values}'" for column, values in zip(columns, values))
        query = f"update public.users set {','.join(sets)} where id = '{user_id}'"
        # print(query)
        self.__execute_query(query, commit=True)

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
            query_email = query + f" where lower(email) = '{email.lower()}'"
            records = self.__execute_query(query_email)
            if records:
                error_list.append('email')
        if alias:
            query_alias = query + f" where lower(alias) = '{alias.lower()}'"
            records = self.__execute_query(query_alias)
            if records:
                error_list.append('alias')
        return error_list

    def insert_user(self, phone, email, alias, name, password, promo_code):
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
        if not promo_code:
            promo_code = 'null'
        else:
            promo_code = f"'{promo_code}'"
        query = f"INSERT INTO public.users(phone, email, alias, name, password,promo_code)	" \
                f"VALUES ({phone},{email},'{alias}',{name},'{password}',{promo_code})"
        print(query)
        self.__execute_query(query, commit=True)

    def get_all_ids(self, id_type):
        ids = []
        query = f'select id from public.{id_type}'
        records = self.__execute_query(query)
        for record in records:
            ids.append(record[0])
        return ids

    def get_empty_request_id(self, user_id):
        query = f"select id from public.requests where user_id = '{user_id}' and request_type = '{self.empty_request_type}'"
        records = self.__execute_query(query)
        if records:
            return records[0][0]
        else:
            return None

    def insert_request(self, user_id, request_type, custom_code=None, product_type=None, doc_type=None,
                       validity_period=None, add_info=None, request_id=None, files=None, short_id=None):
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
        if request_id:
            columns.append('id')
            values.append(request_id)
        if short_id:
            columns.append('short_id')
            values.append(short_id)
        if files:
            columns.append('files')
            files_str = ','.join(files)
            values.append(f"{{{files_str}}}")
        values = list(f"'{v}'" for v in values)
        query = f"INSERT INTO public.requests({','.join(columns)}) VALUES ({','.join(values)}) returning id"
        print(query)
        records = self.__execute_query(query, commit=True, is_return=True)
        return records[0][0]

    def registration_request(self, user_id):
        columns = ['user_id', 'request_type']
        values = [user_id, self.empty_request_type]
        values = list(f"'{v}'" for v in values)
        query = f"INSERT INTO public.requests({','.join(columns)}) VALUES ({','.join(values)}) returning id"
        records = self.__execute_query(query, commit=True, is_return=True)
        return records[0][0]

    def update_request(self, user_id, request_id, custom_code=None, product_type=None, doc_type=None,
                       validity_period=None, add_info=None):
        columns = []
        values = []
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
        sets = (f"{column}='{values}'" for column, values in zip(columns, values))
        query = f"update public.requests set {','.join(sets)} where id = '{request_id}' and user_id = '{user_id}'"
        # print(query)
        self.__execute_query(query, commit=True)

    def get_requests(self, top_count=None, user_id=None, request_id=None, from_dt=None, expert_id=None):
        # statuses = ','.join(f"'{status}'" for status in status_list)
        query = f"""select * from public.requests_view"""
        # where status in ({statuses})"""
        # and request_type = '{request_type}'"""
        where_list = []
        if user_id:
            where_list.append(f"user_id = '{user_id}'")
            # query += f""" where user_id = '{user_id}'"""
        if request_id:
            where_list.append(f"id = '{request_id}'")
            # query += f" and r.id = '{request_id}'"
        if expert_id:
            where_list.append(f"expert_id = '{expert_id}'")
        if from_dt:
            where_list.append(f"update_dt > '{from_dt}'")
        if where_list:
            query += f" where {' and '.join(where_list)}"
        query += f""" order by insert_dt desc """
        if top_count:
            query += f""" limit {top_count}"""
        # print(query)
        records, columns = self.__execute_query(query, is_columns_name=True)
        return records, columns

    def update_request_status(self, request_id, status):
        query = f"""update public.requests set status = {status}, update_dt = CURRENT_TIMESTAMP
                where id = '{request_id}'"""
        self.__execute_query(query, commit=True)

    def add_files_to_request(self, request_id, files):
        files_str = ','.join(files)
        query = f"update requests set files = array_cat(files,'{{{files_str}}}') where id = '{request_id}'"
        self.__execute_query(query, commit=True)

    def get_empty_job_id(self, user_id):
        query = f"""select id from public.projects where user_id = '{user_id}'
                and customer_agreement = '{self.empty_request_type}' and agent_agreement = '{self.empty_request_type}'
                and acts = '{self.empty_request_type}'"""
        records = self.__execute_query(query)
        if records:
            return records[0][0]
        else:
            return None

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

    def registration_job(self, user_id):
        columns = ['user_id', 'customer_agreement', 'agent_agreement', 'acts', 'title', 'custom_code', 'client_price',
                   'cost_price']
        values = [user_id, self.empty_request_type, self.empty_request_type, self.empty_request_type,
                  self.empty_request_type,
                  0, 0, 0]
        values = list(f"'{v}'" for v in values)
        query = f"INSERT INTO public.projects ({','.join(columns)}) VALUES ({','.join(values)}) returning id"
        records = self.__execute_query(query, commit=True, is_return=True)
        return records[0][0]

    def update_job(self, job_id, c_agreement, a_agreement, acts, title, custom_code, client_price, cost_price,
                   request_id=None, description=None):
        columns = ['id', 'customer_agreement', 'agent_agreement', 'acts', 'title', 'custom_code', 'client_price',
                   'cost_price']
        values = [job_id, c_agreement, a_agreement, acts, title, custom_code, client_price, cost_price]
        if request_id:
            columns.append('request_id')
            values.append(request_id)
        if description:
            columns.append('description')
            values.append(description)
        sets = (f"{column}='{values}'" for column, values in zip(columns, values))
        query = f"update public.projects set {','.join(sets)} where id = '{job_id}'"
        # print(query)
        self.__execute_query(query, commit=True)

    def get_jobs(self, top_count, user_id=None):
        # query = f"select * from public.projects"
        # if user_id:
        #     query += f" where user_id = '{user_id}' and customer_agreement != '{self.empty_request_type}' " \
        #              f"and agent_agreement != '{self.empty_request_type}' and acts != '{self.empty_request_type}'"
        # query += f" order by insert_dt desc limit {top_count}"""
        query = f"select * from public.projects_view"
        if user_id:
            query += f" where user_id = '{user_id}'"
        query += f" order by insert_dt desc limit {top_count}"""
        # print(query)
        records, columns = self.__execute_query(query, is_columns_name=True)
        return records, columns

    def get_margins(self, top_count):
        query = f"""select m.*,u.name,u.alias,u.workplace from margin m
                join users u on m.user_id = u.id
                where margin>0
                order by full_price desc limit {top_count}"""
        records, columns = self.__execute_query(query, is_columns_name=True)
        return records, columns

    def insert_notification_token(self, user_id, token):
        query = f"""DO
$do$
BEGIN
IF EXISTS (SELECT * FROM public.tokens where user_id='{user_id}') THEN
update public.tokens set notification = '{token}',update_dt = CURRENT_TIMESTAMP where user_id='{user_id}';
else insert into public.tokens (user_id,notification) Values ('{user_id}','{token}');
END IF;
END
$do$"""
        # query = f"""insert into public.tokens (user_id,notification) VALUES ('{user_id}','{token}')"""
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

    def get_user_role(self, user_id):
        query = f"""select role from roles
                where user_id = '{user_id}'"""
        records = self.__execute_query(query)
        if records:
            return records[0][0]

    def get_user_info(self, user_id):
        query = f"select * from users_view where id = '{user_id}'"
        records, columns = self.__execute_query(query, is_columns_name=True)
        return records[0], columns

    def insert_add_request_info(self, request_id, user_id, required_files=None, price=None, duration=None,
                                description=None):
        columns = ['request_id', 'user_id']
        values = [request_id, user_id]
        subquery_update = []
        if required_files:
            columns.append('required_files')
            files_str = ','.join(required_files)
            values.append(f"{{{files_str}}}")
            subquery_update.append(f"required_files = array_cat(required_files,'{{{files_str}}}')")
        if price:
            columns.append('price')
            values.append(price)
            subquery_update.append(f"price = {price}")
        if duration:
            columns.append('duration')
            values.append(duration)
            subquery_update.append(f"duration = {duration}")
        if description:
            columns.append('description')
            values.append(description)
            subquery_update.append(f"description = {description}")
        values = list(f"'{v}'" for v in values)
        query_insert = f"INSERT INTO public.add_request_info({','.join(columns)}) VALUES ({','.join(values)})"
        query = f"""DO
        $do$
        BEGIN
        IF EXISTS (SELECT * FROM public.add_request_info where request_id = '{request_id}') THEN
        update public.add_request_info set {','.join(subquery_update)} where request_id='{request_id}';
        else {query_insert};
        END IF;
        END
        $do$"""
        print(query)
        self.__execute_query(query, commit=True)

    def get_add_request_info(self, request_id, user_id):
        query = f"select * from add_request_info where request_id = '{request_id}' and user_id = '{user_id}'"
        records, columns = self.__execute_query(query, is_columns_name=True)
        if records:
            return records[0], columns
        else:
            return None, None

    def delete_files_from_add_request_info(self, request_id):
        query = f"update add_request_info set required_files = '{{}}' where request_id = '{request_id}'"
        self.__execute_query(query, commit=True)

    def delete_margin(self):
        query = "delete from margin"
        self.__execute_query(query, commit=True)

    def get_margin_view(self):
        query = "select * from public.margin_view"
        records, columns = self.__execute_query(query, is_columns_name=True)
        if records:
            return records, columns
        else:
            return None, None

    def get_promo_codes(self, promo_code):
        query = f"select * from promos where code = '{promo_code}'"
        records = self.__execute_query(query)
        return records
