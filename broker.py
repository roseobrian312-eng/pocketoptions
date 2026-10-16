"""Read-only Pocket Option QT Demo diagnostic adapter.

No order/BUY/SELL methods are called or exposed. Only start after owner login.
The third-party package is unaffiliated with Pocket Option; use with caution.
"""
import json
import logging
import os
import threading
import time

LOG = logging.getLogger(__name__)

DEFAULT_SYMBOLS = ["EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDUSD_otc", "EURJPY_otc"]


def only_demo_auth(ssid):
    """Fail closed if the provided Socket.IO auth is not explicitly demo."""
    ssid = (ssid or "").strip()
    if not ssid.startswith('42'):
        return False
    try:
        packet = json.loads(ssid[2:])
        if not isinstance(packet, list) or len(packet) < 2 or packet[0] != 'auth':
            return False
        body = packet[1]
        if not isinstance(body, dict):
            return False
        return body.get('isDemo') in (1, True, '1') and bool(body.get('session'))
    except (ValueError, TypeError, KeyError):
        return False


class DemoFeed:
    def __init__(self):
        self.lock = threading.RLock()
        self.client = None
        self.state = 'offline'
        self.message = 'Not connected'
        self.started = False
        raw = os.getenv('OTC_PAIRS', ','.join(DEFAULT_SYMBOLS))
        symbols = [s.strip() for s in raw.split(',') if s.strip().endswith('_otc')]
        self.symbols = list(dict.fromkeys(symbols))[:10] or DEFAULT_SYMBOLS[:]
        self.last_observed = {}
        self.last_value = {}
        self.connected_at = None

    def begin(self):
        secret = os.getenv('PO_SSID', '')
        if not secret:
            return False, 'Add PO_SSID in Render Environment first. Do not paste it in chat or GitHub.'
        if not only_demo_auth(secret):
            return False, 'PO_SSID is not a valid QT Demo auth packet. Real-account sessions are blocked.'
        with self.lock:
            if self.state in ('connecting', 'connected'):
                return True, 'Connection already requested.'
            self.state = 'connecting'
            self.message = 'Connecting to Pocket Option QT Demo (read-only)...'
        threading.Thread(target=self._connect, args=(secret,), daemon=True).start()
        return True, 'Connection started. Wait up to 35 seconds.'

    def _connect(self, ssid):
        try:
            # This library is installed from an external, unofficial GitHub project.
            from pocketoptionapi.stable_api import PocketOption
            client = PocketOption(ssid)
            ok, reason = client.connect()
            if not ok:
                # Auth/session reasons might contain sensitive data; do not log or return verbatim.
                raise RuntimeError('Connection or demo authentication failed. Check Render logs for a sanitized status.')
            with self.lock:
                self.client = client
                self.state = 'connected'
                self.message = 'Socket connected. Waiting for OTC price ticks.'
                self.connected_at = time.time()
            for symbol in self.symbols:
                try:
                    client.subscribe(symbol, period=60)
                    time.sleep(0.35)
                except Exception:
                    LOG.warning('Subscribe failed for %s', symbol)
            with self.lock:
                self.message = 'Subscriptions requested. Awaiting tick verification.'
        except Exception as exc:
            LOG.warning('Demo feed connection failure: %s', type(exc).__name__)
            with self.lock:
                self.client = None
                self.state = 'error'
                self.message = 'Connection failed. Session may be expired, blocked, or the unofficial API may be incompatible.'

    def snapshot(self):
        with self.lock:
            client = self.client
            state = self.state
            message = self.message
            started_at = self.connected_at
        if state == 'connected' and client:
            try:
                if not client.check_connect():
                    state = 'disconnected'
                    message = 'WebSocket disconnected; reconnect from the dashboard.'
            except Exception:
                state = 'disconnected'
                message = 'Connection health could not be verified.'
        catalog = {}
        if state == 'connected' and client:
            try:
                catalog = client.get_assets() or {}
            except Exception:
                catalog = {}
        markets = []
        now = time.time()
        for symbol in self.symbols:
            data = catalog.get(symbol) or {}
            price = None
            count = 0
            received = False
            if state == 'connected' and client:
                try:
                    ticks = client.get_realtime_ticks(symbol, limit=3) or []
                    count = len(ticks)
                    if ticks:
                        ts, raw_price = ticks[-1]
                        price = float(raw_price)
                        # Compare tick signature; server clock may have a UTC offset.
                        signature = (str(ts), str(raw_price))
                        with self.lock:
                            if self.last_value.get(symbol) != signature:
                                self.last_value[symbol] = signature
                                self.last_observed[symbol] = now
                            age = now - self.last_observed.get(symbol, 0)
                        received = age <= 20
                except Exception:
                    pass
            payout = data.get('payout') if isinstance(data, dict) else None
            availability = data.get('is_available') if isinstance(data, dict) else None
            markets.append({
                'symbol': symbol, 'name': symbol.replace('_otc', ' OTC'),
                'price': price, 'ticks_sampled': count,
                'feed': 'receiving' if received else ('waiting' if state == 'connected' else 'offline'),
                'payout': payout if isinstance(payout, (float, int)) else None,
                'available': availability if isinstance(availability, bool) else None,
            })
        return {
            'state': state,
            'message': message,
            'broker': 'Pocket Option (unofficial)',
            'mode': 'QT Demo — read-only',
            'orders_enabled': False,
            'streaming_count': sum(m['feed'] == 'receiving' for m in markets),
            'markets': markets,
            'connected_seconds': round(now - started_at) if started_at else None,
            'observed_at': int(now),
        }


feed = DemoFeed()
