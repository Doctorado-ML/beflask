import os
from dotenv import load_dotenv

dotenv_file = ".env"
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, dotenv_file))


class Config(object):
    COMPARE = os.environ.get("COMPARE") == "True" or False
    TEMPLATES_AUTO_RELOAD = True
    SECRET_KEY = os.environ.get("SECRET_KEY") or "really-hard-to-guess-key"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
