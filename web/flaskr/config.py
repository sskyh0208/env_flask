import os
basedir = os.path.abspath(os.path.dirname(__name__))

class BaseConfig(object):
    DEBUG = True
    TESTING = False
    DB_USERNAME = 'yoshihiro'
    DB_PASSWORD = 'P@ssssskyh0208'
    DB_HOST = 'localhost'
    DB_SCHEMA = 'flask'
    SECRET_KEY = 'mysite'
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_SCHEMA}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevConfig(object):
    DEBUG = True
    TESTING = False
    SECRET_KEY = 'mysite'
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'data.sqlite')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
