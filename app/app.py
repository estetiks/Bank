from flask import Flask
from config import Config
from flask_login import LoginManager
from models import db, Users
from routers import *
from create_admin import create_admin



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    with app.app_context():
        db.create_all()
        create_admin(db)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))
    
    app.register_blueprint(bp)

    app.run(debug=False,host='0.0.0.0', port=5000)


if __name__ == "__main__":
    create_app()

