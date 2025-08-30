from flask import Blueprint, render_template_string

mobile_preview_bp = Blueprint('mobile_preview', __name__)

@mobile_preview_bp.route('/mobile-preview')
def mobile_preview():
    with open('mobile_preview.html', 'r') as f:
        html_content = f.read()
    return html_content