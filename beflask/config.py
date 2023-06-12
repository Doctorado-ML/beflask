import os
from dotenv import load_dotenv
import benchmark
from beflask import __version__


def get_base_dir():
    return os.path.abspath(os.path.dirname(__file__))


dotenv_file = ".env"
file_name = os.path.join(get_base_dir(), dotenv_file)
load_dotenv(file_name)


class Config(object):
    COMPARE = os.environ.get("COMPARE") == "True" or False
    TEMPLATES_AUTO_RELOAD = True
    SECRET_KEY = os.environ.get("SECRET_KEY") or "really-hard-to-guess-key"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(get_base_dir(), "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    INDEX = "main.index"
    APP_VERSION = __version__
    BENCHMARK_VERSION = benchmark.__version__
    DEBUG = os.environ.get("DEBUG") == "True" or False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    WTF_CSRF_ENABLED = False
    SOCKETIO_MESSAGE_QUEUE = None


# class Config(object):
#     DEBUG = False
#     TESTING = False
#     SECRET_KEY = os.environ.get(
#         "SECRET_KEY", "51f52814-0071-11e6-a247-000ec6c2372c"
#     )
#     SQLALCHEMY_DATABASE_URI = os.environ.get(
#         "DATABASE_URL", "sqlite:///" + os.path.join(basedir, "db.sqlite")
#     )
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     REQUEST_STATS_WINDOW = 15
#     CELERY_CONFIG = {}
#     SOCKETIO_MESSAGE_QUEUE = os.environ.get(
#         "SOCKETIO_MESSAGE_QUEUE",
#         os.environ.get("CELERY_BROKER_URL", "redis://"),
#     )


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
