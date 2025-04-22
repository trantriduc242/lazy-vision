from flask import Flask

def create_app():
    app = Flask(__name__, static_folder="../static")  # <-- key line
    app.config['SECRET_KEY'] = 'lazyvision_secret'

    from .routes import bp
    app.register_blueprint(bp)

    return app
