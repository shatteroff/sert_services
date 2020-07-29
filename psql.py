from Helper import Helper
from PsqlHelper import PsqlHelper

ph = PsqlHelper()
h = Helper()

# print(ph.get_login("89035555555", 12345))
# print(ph.get_login("bobsik@mail.ru", 5))
# ph.insert_user(89050000001, 'y@mail.com', 'ygrik',None, 12345)
# ph.get_all_jobs_id()
# ph.insert_request("6df766be-d3fe-4a4e-823d-fbc3476e7df5", 'email', None, 'ретля', None, '5', None)
h.request_registration({'user_id': "6df766be-d3fe-4a4e-823d-fbc3476e7df5",
                        'request_type': 'email',
                        'product_type': 'window',
                        'validity_period': 7})
