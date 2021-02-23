# import json
#
# import firebase_admin
# from firebase_admin import credentials, messaging
#
# try:
#     from Config import Config
# except:
#     from Config_local import Config
#
#
# class FirebaseHelper:
#
#     def send_notification(self, client_token, title, body):
#         token = Config.fb_token.replace('\n', '\\n')
#         token = json.loads(token)
#         cred = credentials.Certificate(token)
#         firebase_admin.initialize_app(cred)
#         message = messaging.Message(notification=messaging.Notification(
#             title=title, body=body,
#         ), token=client_token)
#         response = messaging.send(message)
#         return response
