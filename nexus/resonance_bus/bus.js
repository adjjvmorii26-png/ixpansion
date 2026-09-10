const listeners = new Map();
const history = [];
function subscribe(event, fn) {
  if (!listeners.has(event)) listeners.set(event, []);
  listeners.get(event).push(fn);
}
function publish(event, payload = {}) {
  const entry = { event, payload, ts: Date.now() };
  history.push(entry);
  if (history.length > 200) history.shift();
  (listeners.get(event) || []).forEach(fn => { try { fn(payload); } catch (e) {} });
  (listeners.get("*") || []).forEach(fn => { try { fn(entry); } catch (e) {} });
}
function recent(n = 10) { return history.slice(-n); }
module.exports = { subscribe, publish, recent };
