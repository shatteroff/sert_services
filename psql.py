from Helper import Helper
from PsqlHelper import PsqlHelper

ph = PsqlHelper()
h = Helper()

# print(ph.get_login("89035555555", 12345))
# print(ph.get_login("bobsik@mail.ru", 5))
# ph.insert_user(89050000001, 'y@mail.com', 'ygrik',None, 12345)
# ph.get_all_jobs_id()
# ph.insert_request("6df766be-d3fe-4a4e-823d-fbc3476e7df5", 'email', None, 'ретля', None, '5', None)
# h.request_registration({'user_id': "6df766be-d3fe-4a4e-823d-fbc3476e7df5",
#                         'request_type': 'email',
#                         'product_type': 'window',
#                         'validity_period': 7})
# record_list = []
#
# records, columns = ph.get_requests('1821f722-8f2e-449a-b37e-b10f2ec07039', 5, ['new'])
# print(columns)
# print(records[0][5])
# for record in records:
#     request_new_dict = {}
#     for i in range(len(columns) - 1):
#         print(i)
#         request_new_dict.update({columns[i]: record[i]})
#     request_new_dict.update({"date": record[len(columns)-1].date()})
#     record_list.append(request_new_dict)
# print(record_list)
h.get_user_requests({"user_id": '1821f722-8f2e-449a-b37e-b10f2ec07039', 'count': 5})
