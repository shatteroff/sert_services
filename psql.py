from PsqlHelper import PsqlHelper

ph = PsqlHelper()
print(ph.get_login("89035555555", 12345))
print(ph.get_login("bobsik@mail.ru", 5))
ph.insert_user(89050000001, "'y@mail.com'", "'ygrik'", 'null', 12345)
