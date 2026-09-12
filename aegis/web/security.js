const AegisSecurity = {
  async scan() {
    const path = document.getElementById('scanPath').value.trim();
    if (!path) return;
    const out = document.getElementById('scanResult');
    out.textContent = 'Scanning selected file...';
    try {
      const r = await fetch('/api/security/scan', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({path})});
      const data = await r.json();
      out.textContent = JSON.stringify(data, null, 2);
      if (data.verdict === 'MALICIOUS' || data.verdict === 'REVIEW') {
        await fetch('/api/events', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({title:`File scan: ${data.verdict}`, severity:data.verdict === 'MALICIOUS' ? 'HIGH':'MEDIUM', source:'malware-scanner', details:data.path})});
      }
    } catch (e) { out.textContent = String(e); }
  },
  async overview() {
    try { document.getElementById('scannerStatus').textContent = JSON.stringify(await (await fetch('/api/security/scanner')).json(), null, 2); } catch(e) {}
  }
};
AegisSecurity.overview();
