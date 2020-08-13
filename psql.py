from Helper import Helper
from PsqlHelper import PsqlHelper

ph = PsqlHelper()
h = Helper()
# test PsqlHelper.insert_job
# req_id = ph.insert_request('1821f722-8f2e-449a-b37e-b10f2ec07039', 'email')
# print(ph.insert_job('1821f722-8f2e-449a-b37e-b10f2ec07039', True, True, True, 'Труба', 1234, 100, 200, req_id,
#                     "Описание"))

# test Helper.job_registration
# job_dict = {'user_id': '1821f722-8f2e-449a-b37e-b10f2ec07039', 'customer_agreement': True, 'agent_agreement': True,
#             'acts': True, 'title': 'Тест работ', 'custom_code': 1234, 'client_price': 100, 'cost_price': 200}
# print(h.job_registration(job_dict))

