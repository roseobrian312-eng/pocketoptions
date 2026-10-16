'use strict';
const $ = id => document.getElementById(id);
const priceText = n => Number.isFinite(n) ? String(n) : '—';
const safe = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

async function refreshFeed() {
  try {
    const r = await fetch('/api/status', {cache:'no-store'});
    if (r.status === 401) { location.href = '/login'; return; }
    if (!r.ok) throw new Error('Status unavailable (' + r.status + ')');
    const d = await r.json();
    $('top-status').textContent = '● ' + String(d.state || 'offline').toUpperCase();
    $('broker').textContent = d.state === 'connected' ? 'Connected' : 'None';
    $('connection-msg').textContent = d.message || 'No message';
    $('streaming').textContent = d.streaming_count;
    $('data-status').textContent = d.streaming_count ? 'TICKS RECEIVED' : 'NO VERIFIED TICKS';
    $('markets').innerHTML = d.markets.map(m => {
      const mode = m.feed === 'receiving' ? 'RECEIVING' : m.feed === 'waiting' ? 'WAITING' : 'OFFLINE';
      return `<tr><td><span class="dot ${m.feed === 'receiving' ? 'live' : ''}"></span>${safe(m.name)}</td><td>${priceText(m.price)}</td><td>${m.payout === null ? '—' : Number(m.payout).toFixed(0) + '%'}</td><td><span class="chip">${mode}</span></td></tr>`;
    }).join('');
    $('server').textContent = 'Read-only QT Demo diagnostics · Server update ' + new Date().toLocaleTimeString();
  } catch (e) { $('server').textContent = 'Feed status error: ' + e.message; }
}

$('connect-btn').addEventListener('click', async () => {
  const btn = $('connect-btn'); btn.disabled = true;
  $('action-result').textContent = 'Requesting QT Demo connection…';
  try {
    const r = await fetch('/api/connect', {method:'POST', headers:{'Content-Type':'application/json'},body:'{}'});
    const d = await r.json();
    $('action-result').textContent = d.message || d.error || 'No response';
  } catch (e) { $('action-result').textContent = 'Connection request failed: ' + e.message; }
  finally { btn.disabled = false; refreshFeed(); }
});

refreshFeed();
setInterval(refreshFeed, 4000); // Reads local buffered ticks only. No additional broker subscription per poll.
