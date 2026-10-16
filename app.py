"""Market Shaker AI 0.2: owner-protected, read-only QT Demo feed diagnostics."""
import hmac
import os
import secrets
import time
from datetime import timedelta
from functools import wraps

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from broker import feed

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY') or secrets.token_hex(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=(os.getenv('RENDER', '').lower() == 'true'),
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
)

# Small single-process login throttle; replace with centralized rate limiting before selling.
attempts = {}


def owner_only(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        if not os.getenv('ADMIN_PASSWORD'):
            return render_template('setup.html'), 503
        if not session.get('owner'):
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Login required'}), 401
            return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return inner


@app.get('/health')
def health():
    return jsonify({'status': 'ok', 'orders_enabled': False})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if not os.getenv('ADMIN_PASSWORD'):
        return render_template('setup.html'), 503
    if request.method == 'POST':
        source = request.remote_addr or 'unknown'
        history = [t for t in attempts.get(source, []) if time.time() - t < 300]
        if len(history) >= 5:
            return render_template('login.html', error='Too many attempts. Try again after 5 minutes.'), 429
        entered = (request.form.get('password') or '')
        if hmac.compare_digest(entered.encode(), os.environ['ADMIN_PASSWORD'].encode()):
            attempts.pop(source, None)
            session.clear()
            session['owner'] = True
            session.permanent = True
            return redirect(url_for('home'))
        history.append(time.time())
        attempts[source] = history
        return render_template('login.html', error='Incorrect password.'), 401
    return render_template('login.html', error=None)


@app.post('/logout')
@owner_only
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.get('/')
@owner_only
def home():
    return render_template('index.html', has_ssid=bool(os.getenv('PO_SSID')))


@app.get('/api/status')
@owner_only
def status():
    return jsonify(feed.snapshot())


@app.post('/api/connect')
@owner_only
def connect():
    # Check Content-Type and browser Origin when present to reduce cross-site triggers.
    origin = request.headers.get('Origin', '')
    if origin and not origin.rstrip('/').endswith(request.host):
        return jsonify({'error': 'Origin rejected'}), 403
    ok, msg = feed.begin()
    return jsonify({'ok': ok, 'message': msg}), 202 if ok else 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '10000')))
