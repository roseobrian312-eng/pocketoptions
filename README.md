# Market Shaker AI — OTC Scanner Dashboard Prototype

A Render-ready Flask UI prototype for a future Pocket Option QT Demo OTC scanner.

**Important:** This version does NOT connect to Pocket Option, retrieve live OTC prices, produce real signals, or place trades. All displayed instruments are placeholders. No credentials are needed.

## Deploy on Render

1. Push these files to your **private** GitHub repository, preserving the `templates/` and `static/` folders.
2. Render → New → Web Service → connect repository.
3. Language: Python 3. Build command: `pip install -r requirements.txt`.
4. Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`.
5. Select Free if available and deploy. The free tier may sleep after inactivity.

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Visit http://localhost:10000

## Before trading integration

Confirm Pocket Option terms and supported execution methods; independently verify live OTC data, test one genuine QT Demo order and settlement, implement loss limits and trade auditing. Never commit session cookies, passwords, or API keys to GitHub.
