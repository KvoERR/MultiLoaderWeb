import sys
import os

INTERP = os.path.expanduser("/var/www/u3449615/data/www/multiloader.ru/MultiLoader/venv/bin/python")

if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd())

from app import app
from models import init_db

init_db()

application = app
