const samples = ['EUR/USD OTC','GBP/JPY OTC','USD/JPY OTC','AUD/CAD OTC','EUR/GBP OTC','GBP/USD OTC'];
document.getElementById('markets').innerHTML = samples.map(name => `<tr><td><span class="dot"></span>${name}</td><td>—</td><td class="muted">NO DATA</td><td><span class="chip">DISCONNECTED</span></td></tr>`).join('');
fetch('/api/status').then(r => r.json()).then(data => {
  document.getElementById('server').textContent = `Server online · ${data.mode} · ${data.message}`;
}).catch(() => document.getElementById('server').textContent = 'Could not reach application status endpoint.');
