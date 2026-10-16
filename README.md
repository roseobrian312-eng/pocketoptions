# Market Shaker AI 0.2 — QT Demo OTC connection test

This is **NOT** an auto-trading bot yet. A Flask dashboard displays **only actual tick values** fetched through an unofficial Pocket Option API. There are no BUY/SELL order calls anywhere in the program. If data isn't available, it clearly says *waiting/offline* instead of showing invented values.

## Deploy on Render

Upload ALL files at the root of your existing private `pocketoptions` GitHub repository, replacing the first prototype's files. Keep the `templates/` and `static/` folders. Render deploy settings:

- Language: Python 3
- Build: `pip install -r requirements.txt`
- Start: `gunicorn app:app --workers 1 --threads 4 --bind 0.0.0.0:$PORT`
- Instance: Free for development only. Free services sleep and **cannot be trusted for 24/7 trading**.
- Python: `.python-version` pins Python 3.11.11.

## Render Environment variables

Use Render → your Web Service → Environment. **Never put any secrets in GitHub or send them in a chat/screenshot.**

1. **`ADMIN_PASSWORD`**: A long password you choose. Required before ANY dashboard can load. Users of the public Render URL will see only a login prompt.
2. **`FLASK_SECRET_KEY`**: Random long string for Flask session signing (strongly recommended). Keep it stable across deploys.
3. **`PO_SSID`**: Full Socket.IO authentication packet from a **QT Demo session only**. It is equivalent to a login credential and may allow account access. Obtain only from your own account and place it directly into Render Environment, never a file. Do not submit it to a third party. Leave unset until you review the unofficial library and accept the risk.
4. Optional **`OTC_PAIRS`**: e.g., `EURUSD_otc,GBPUSD_otc,USDJPY_otc,AUDUSD_otc,EURJPY_otc`. Max 10 demo OTC symbols.

After saving env settings, Render may redeploy the service. Sign in, click **Connect QT Demo feed**, then allow up to 35 seconds. Watch pair statuses: **RECEIVING** means real per-symbol tick updates were observed; **WAITING** means not yet confirmed. A connected socket does not guarantee that OTC prices are arriving.

## Security and scope

- This package uses `chema-creator/PocketOptionApi`, an **unofficial** third-party library. Its `PocketOption` class also exposes order methods, but this package never calls them. Do not assume the library is vetted or the broker approves it. Its README documents disabled `requests` TLS verification in one HTTP helper; audit and harden before production.
- The broker SDK uses module globals and background threads, so the supplied Gunicorn command deliberately runs one worker. Data disappears on Render sleep or redeploy.
- The backend rejects auth packets unless `isDemo` is explicitly true/1 and a nonempty `session` is present. It has no path to executing an order, even on demo.
- Do **not** set `PO_SSID` using a real-money session. Never share it with support chats, screenshots, untrusted plugins, or public code.
- Test with a disposable demo-only account if possible, and always verify account status from the broker UI.
- For commercial release add persistent databases, independent authentication, hardened deployment, token rotation, customer isolation, broker compliance checks, audit logs and extensive safety testing.

## Workflow

1. Deploy and secure the dashboard.
2. Verify price updates; confirm prices match the Pocket Option QT Demo screen.
3. Build and backtest a transparent ranking algorithm; the current prototype makes no signal/AI recommendations.
4. Only after separate approval, reliability testing and safeguards, investigate demo order submission and settlement.
