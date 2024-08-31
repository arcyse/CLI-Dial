from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

#* The presence of this  __init__.py file makes the website directory a python package
#* Hence, website can be imported as a package in main

# Create an instance of SQLAlchemy (database):
db = SQLAlchemy()
DB_NAME = 'database.db' # some arbritrary name for the database

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret-key-goes-here' #TODO: See how to adjust this
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}' # Configure the app to use the created database
    db.init_app(app) # Let the database know which app it is associated with

    # Register blueprints for the views and auth during app creation:
    from .views import views #.views -> '.' refers to current python package and 'views' refers to filename
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/') # No url prefix

    # Create database (if not already created):
    from .models import User # Stores information about the classes / DB structure

    create_database(app)

    # Login-related details
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id)) # Already knows that id is primary key (by default)

    return app

def create_database(app):
    with app.app_context():
        if not path.exists('instance/' + DB_NAME):
            db.create_all()
            print('Created Database!')



'''
From stack overflow: 
"There is no need for that create_database function. 
SQLAlchemy will already not overwrite an existing file, and the only
time the database wouldn't be created is if it raised an error."
'''