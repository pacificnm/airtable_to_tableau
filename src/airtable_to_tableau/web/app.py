from flask import Flask
from .routes import routes  # Import the Blueprint

def create_app():
    app = Flask(__name__)
    app.secret_key = "your-secret-key"  # Needed for flash messages

    # ✅ Register the Blueprint
    app.register_blueprint(routes)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
