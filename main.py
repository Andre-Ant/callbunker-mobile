from app import app
from flask import send_from_directory, render_template_string
import os

# Add mobile web testing route
@app.route('/mobile')
def mobile_demo():
    try:
        with open('mobile_app/web/index.html', 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return render_template_string('''
        <h1>Mobile Demo Loading...</h1>
        <p>Setting up CallBunker mobile demo...</p>
        <script>window.location.reload();</script>
        ''')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
