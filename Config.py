import os


class Config:
    psql_url = os.environ['DATABASE_URL']
    fb_token = os.environ['FIREBASE_TOKEN']
    SECRET_KEY = os.environ['SECRET_KEY']
    YANDEX_TOKEN = os.environ['YANDEX_TOKEN']
