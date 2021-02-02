from flask import Flask
from flask_cors import CORS
# http://flask.pocoo.org/docs/0.10/patterns/appfactories/


def create_app(config_filename):
    app = Flask(__name__, static_folder='templates/static')
    CORS(app)
    app.config.from_object(config_filename)

    # Init Flask-SQLAlchemy
    from app.basemodels import db
    db.init_app(app)

    from app.baseviews import login_required, login1, mail
    from flask import render_template, send_from_directory
    import os

    # Init Flask-Mail
    mail.init_app(app)

    @app.route('/<path:filename>')
    def file(filename):
        return send_from_directory(os.path.join(app.root_path, 'templates/static/dist'), filename)
    
    #app-route
    @app.route('/users')
    @app.route('/')
    @app.route('/login')
    def index():
        return render_template('static/dist/index.html')

    


    # Auth API
    app.register_blueprint(login1, url_prefix='/api/v1/')

 

    # Blueprints
    from app.users.views import users
    app.register_blueprint(users, url_prefix='/api/v1/users')
    

    return app
