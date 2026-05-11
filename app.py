from flask import Flask, render_template
from config import Config
from routes.user import user_bp
from routes.projects import projects_bp
from routes.backings import backings_blueprint
import base64


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['DEBUG'] = True

    @app.route("/")
    def home():
        return render_template("index.html")

    app.register_blueprint(user_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(backings_blueprint)
    
    # Add b64encode filter for Jinja2
    def b64encode_filter(x):
        if isinstance(x, bytes):
            return base64.b64encode(x).decode('utf-8')
        return ''
    app.jinja_env.filters['b64encode'] = b64encode_filter

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
