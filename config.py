"""Flask konfigurācija"""

from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

class Config:
    SECRET_KEY = environ.get("SECRET_KEY")
    MAINTENANCE_MODE = True if environ.get('MAINTENACE_MODE') == 'true' else False
    FLASK_ENV = environ.get("FLASK_ENV")
    STATIC_FOLDER = 'static'
    STATIC_URL_PATH = '/static'
    UPLOAD_FOLDER = 'static/images'

    #MYSQL_DATABASE_HOST = environ.get('MYSQL_DATABASE_HOST')
    #MYSQL_DATABASE_USER = environ.get('MYSQL_DATABASE_USER')
    #MYSQL_DATABASE_PASSWORD = environ.get('MYSQL_DATABASE_PASSWORD')
    #MYSQL_DATABASE_DB = environ.get('MYSQL_DATABASE_DB')
    #MYSQL_DATABASE_PORT = environ.get('MYSQL_DATABASE_PORT')

    #SQLALCHEMY_DATABASE_URI = f"mysql://{MYSQL_USER}:{MYSQL_PW}@{MYSQL_URL}:{MYSQL_PORT}/{MYSQL_DB}"



class DevConfig(Config):
    pass

class ProConfig(Config):
    pass