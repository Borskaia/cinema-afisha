from flask import Flask
# from .config import Config


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'

    from .views import view
    from .auth import auth
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(view, url_prefix='/')

    return app
