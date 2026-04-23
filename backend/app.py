import sys
import os

# Add the parent directory to sys.path so we can import from the model package
current_module_dir = os.path.dirname(os.path.abspath(__file__))
parent_module_dir = os.path.dirname(current_module_dir)
sys.path.append(parent_module_dir)

from flask import Flask, send_from_directory
from flask_cors import CORS
from routes.analyze import analyze_blueprint

# Creates and configures the Flask application
def create_app():
    """
    Initializes the Flask application, enables CORS,
    and registers the blueprints for routing.
    
    Returns:
        Flask app instance
    """
    try:
        # Configuration for serving the React frontend after build
        frontend_dist_dir = os.path.join(parent_module_dir, "frontend", "dist")
        app = Flask(__name__, static_folder=frontend_dist_dir, static_url_path="/")
        CORS(app)
        
        # Register the analyze route group
        app.register_blueprint(analyze_blueprint)
        
        # Catch-all route to serve the React app
        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def serve_frontend(path):
            if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
                return send_from_directory(app.static_folder, path)
            else:
                return send_from_directory(app.static_folder, "index.html")
                
        return app
    except Exception as e:
        print("Error creating Flask app:")
        print(e)
        return None

if __name__ == "__main__":
    app_instance = create_app()
    if app_instance is not None:
        app_instance.run(host="0.0.0.0", port=5000, debug=True)
