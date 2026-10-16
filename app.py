"""Market Shaker AI prototype dashboard. No broker connection or order execution."""
import os
from datetime import datetime, timezone
from flask import Flask, jsonify, render_template

app = Flask(__name__)

@app.get('/')
def home():
    return render_template('index.html')

@app.get('/api/status')
def status():
    return jsonify({
        'application': 'Market Shaker AI',
        'mode': 'UI_ONLY',
        'scanner_connected': False,
        'broker_connected': False,
        'orders_enabled': False,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'message': 'Dashboard prototype. No live OTC market data or trading connection.'
    })

@app.get('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '10000')))
