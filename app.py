from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

from routes.default import main_bp
from routes.register import register_bp
from routes.close import close_bp
from routes.open import open_bp
from routes.progress_tracking import progressTracking_bp

app.register_blueprint(main_bp)
app.register_blueprint(register_bp)
app.register_blueprint(close_bp)
app.register_blueprint(open_bp)
app.register_blueprint(progressTracking_bp)

if __name__ == "__main__":
    app.run(debug=True)




