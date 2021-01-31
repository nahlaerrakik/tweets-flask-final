__author__ = 'nahla.errakik'

import os

db_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database')


class Config(object):
    ENV = 'production'

    DEBUG = False
    TESTING = False

    SECRET_KEY = 'xyz'

    SESSION_COOKIE_SECURE = False

    TWITTER_API_CLIENT_KEY = 'XCo5wi6tppr98tvsdgJ328CVW'
    TWITTER_API_CLIENT_SECRET = 'zzgcg14Kopv1WzTayRCMWtKM05wXP2MOAJ4McCoVW5oppolbtL'

    ERROR_MSG = 'Oops, something went wrong: {}. Please retry again !'


class ProdConfig(Config):
    DB_NAME = 'prod.db'
    DB_PATH = os.path.join(db_dir, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DB_PATH)
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(Config):
    DEBUG = True

    DB_NAME = 'dev.db'
    DB_PATH = os.path.join(db_dir, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DB_PATH)
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    TESTING = True

    DB_NAME = 'test.db'
    DB_PATH = os.path.join(db_dir, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DB_PATH)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
