import os
import re
from functools import wraps
from flask import request, redirect, url_for, flash, session, abort
from typing import Tuple, Optional

def norm_digits(s: str) -> str:
    """Extract only digits from a string"""
    return re.sub(r"\D", "", s or "")

def norm_speech(s: str) -> str:
    """Normalize speech input for comparison"""
    if not s:
        return ""
    # Remove extra punctuation and normalize spaces
    import re
    normalized = re.sub(r'[^\w\s]', '', s.strip().lower())
    return re.sub(r'\s+', ' ', normalized).strip()

def parse_annotated_number(s: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse number with optional PIN annotation.
    Accepts formats like "617-123-1213 * 1122" or "# 4455"
    Returns (clean_number, pin|None)
    """
    if not s:
        return None, None
    
    # Look for pattern: number followed by * or # and 4 digits
    match = re.match(r"\s*([\+\d][\d\-\s\(\)]*?)\s*[*#]\s*(\d{4})\s*$", s)
    if not match:
        # No PIN annotation, just clean the number
        clean_number = re.sub(r"[^\d+]", "", s)
        return clean_number, None
    
    number_raw, pin = match.group(1), match.group(2)
    clean_number = re.sub(r"[^\d+]", "", number_raw)
    return clean_number, pin

def require_admin_web(f):
    """
    Decorator for web routes that require admin authentication.
    Uses session-based auth for web interface.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if admin token is configured
        admin_token = os.getenv("ADMIN_TOKEN")
        if not admin_token:
            # No admin token configured, allow access
            return f(*args, **kwargs)
        
        # Check session for authentication
        if not session.get('admin_authenticated'):
            # Check for token in request (for initial auth)
            provided_token = request.args.get('token') or request.form.get('token')
            if provided_token == admin_token:
                session['admin_authenticated'] = True
                return f(*args, **kwargs)
            
            # Not authenticated, show simple auth form
            if request.method == 'POST' and 'admin_token' in request.form:
                if request.form['admin_token'] == admin_token:
                    session['admin_authenticated'] = True
                    return f(*args, **kwargs)
                else:
                    flash('Invalid admin token!', 'error')
            
            # Return simple auth form
            return '''
            <html>
            <head>
                <title>Admin Authentication</title>
                <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
            </head>
            <body class="bg-dark text-light">
                <div class="container mt-5">
                    <div class="row justify-content-center">
                        <div class="col-md-6">
                            <div class="card bg-secondary">
                                <div class="card-header">
                                    <h3>Admin Authentication Required</h3>
                                </div>
                                <div class="card-body">
                                    <form method="post">
                                        <div class="mb-3">
                                            <label for="admin_token" class="form-label">Admin Token</label>
                                            <input type="password" class="form-control" name="admin_token" required>
                                        </div>
                                        <button type="submit" class="btn btn-primary">Login</button>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            ''', 401
        
        return f(*args, **kwargs)
    return decorated_function

def require_admin_api(f):
    """
    Decorator for API routes that require admin authentication.
    Uses Bearer token authentication.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_token = os.getenv("ADMIN_TOKEN")
        if not admin_token:
            # No admin token configured, allow access
            return f(*args, **kwargs)
        
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            abort(401, description="Missing or invalid Authorization header")
        
        provided_token = auth_header.split(" ", 1)[1].strip()
        if provided_token != admin_token:
            abort(403, description="Invalid token")
        
        return f(*args, **kwargs)
    return decorated_function
