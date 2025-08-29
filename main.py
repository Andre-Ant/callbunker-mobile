from app import app
from flask import send_from_directory
import os

# Add mobile web testing route
@app.route('/mobile')
def mobile_demo():
    return send_from_directory('mobile_app/web', 'index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
