import os


class Config:
    psql_url = os.environ['DATABASE_URL']
    fb_token = os.environ['FIREBASE_TOKEN']
