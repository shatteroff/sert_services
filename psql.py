from Helper import Helper
from PsqlHelper import PsqlHelper

ph = PsqlHelper()
h = Helper()

# test PsqlHelper.update_request_status
# ph.update_request_status('42ce88a7-d328-4e68-b4b0-3f9a9593cc8a', '0c03c3cf-1b7e-4dab-b5e3-7308c72b2881', 1)

# test Helper.update_request_status
# request_dict = {"user_id": '42ce88a7-d328-4e68-b4b0-3f9a9593cc8a', "request_id": '0c03c3cf-1b7e-4dab-b5e3-7308c72b2881',
#                 "status": 999}
# print(h.update_request_status(request_dict))

# test PsqlHelper.insert_job
# req_id = ph.insert_request('a8bf9f69-98af-4cd1-a19a-20cf36d223d2', 'email')
# print(ph.insert_job('a8bf9f69-98af-4cd1-a19a-20cf36d223d2', True, True, True, 'Труба', 1234, 100, 300, req_id,
#                     "Описание"))

# test Helper.job_registration
# job_dict = {'user_id': '1821f722-8f2e-449a-b37e-b10f2ec07039', 'customer_agreement': True, 'agent_agreement': True,
#             'acts': True, 'title': 'Тест работ', 'custom_code': 1234, 'client_price': 100, 'cost_price': 200}
# print(h.job_registration(job_dict))

# test PsqlHelper.get_jobs
# records, columns = ph.get_jobs('1821f722-8f2e-449a-b37e-b10f2ec07039', 2)
# print(records, columns)

# test Helper.get_user_jobs
# print(h.get_user_jobs('1821f722-8f2e-449a-b37e-b10f2ec07039',None))

# test Helper.get_user_requests
# print(h.get_user_requests('a8bf9f69-98af-4cd1-a19a-20cf36d223d2', None))

# test PsqlHelper.get_margins
# print(ph.get_margins())

# test Helper.get_leader_board
# print(h.get_leader_board(1))

# test Psqlhelper.insert_notification_token
# ph.insert_notification_token('056a062c-6e96-419d-9092-8436564031fa','eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiJiMDhmODZhZi0zNWRhLTQ4ZjItOGZhYi1jZWYzOTA0NjYwYmQifQ.-xN_h82PHVTCMA9vdoHrcZxH-x5mb11y1537t3rGzcM')

# test PsqlHelper.update_notification_token
# ph.update_notification_token('056a062c-6e96-419d-9092-8436564031fa','000000iOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiJiMDhmODZhZi0zNWRhLTQ4ZjItOGZhYi1jZWYzOTA0NjYwYmQifQ.-xN_h82PHVTCMA9vdoHrcZxH-x5mb11y1537t3rGzcM')
