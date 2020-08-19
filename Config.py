import os


class Config:
    psql_url = os.inviron['DATABASE']
    fb_token = os.inviron['FIREBASE_TOKEN']
