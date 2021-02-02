from flask.ext.script import Manager

from app import create_app
from app import db

app = create_app()
manager = Manager(app)

if __name__ == '__main__':
    manager.run()
