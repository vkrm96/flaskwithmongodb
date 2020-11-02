import os

class Config(object):
    SECRET_KEY= os.environ.get('SECRET_KEY') or b'\x98\x92\xfc\xf3\xcd$\x86\xd99c\x97\x80\xc6z\x99\x9d'

    MONGODB_SETTINGS = { 'db' : 'UTA_Enrollement',
    }
