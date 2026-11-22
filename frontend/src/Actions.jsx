import { useState, useEffect } from "react";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8001";

export function Reminders() {
  const [items, setItems] = useState([]);

  async function load() {
    try {
      const r = await fetch(`${API}/reminders`);
      setItems(await r.json());
    } catch (e) {}
  }

  useEffect(() => {
    load();
    window.addEventListener("reminders-changed", load);
    return () => window.removeEventListener("reminders-changed", load);
  }, []);

  if (!items.length) return null;

  return (
    <div className="reminders">
      <h3>Your reminders</h3>
      {items.map((r) => {
        const days = Math.ceil((new Date(r.date) - new Date()) / 86400000);
        const label = days < 0 ? "overdue" : days === 0 ? "today" : `${days} days left`;
        return (
          <div key={r.id} className={`rem ${days <= 3 ? "urgent" : ""}`}>
            <strong>{r.scheme_name}</strong> - {r.date} ({label})
            {r.note && <span className="where"> {r.note}</span>}
          </div>
        );
      })}
    </div>
  );
}

export default function Actions({ scheme, profile }) {
  const [name, setName] = useState("");
  const [date, setDate] = useState("");
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);
  const [auto, setAuto] = useState(null);

  async function downloadPdf() {
    try {
      const res = await fetch(`${API}/form/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scheme_id: scheme.id, name, profile }),
      });
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${scheme.id}-application.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setMsg("Could not create the PDF.");
    }
  }

  async function saveReminder() {
    if (!date) { setMsg("Pick a date first."); return; }
    try {
      await fetch(`${API}/reminders`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scheme_id: scheme.id, scheme_name: scheme.name, date }),
      });
      setMsg("Reminder saved.");
      window.dispatchEvent(new Event("reminders-changed"));
    } catch (e) {
      setMsg("Could not save the reminder.");
    }
  }

  async function runAutomation() {
    setBusy(true);
    setAuto(null);
    setMsg("Agent is filling the demo portal in a browser window...");
    try {
      const res = await fetch(`${API}/automation/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scheme_id: scheme.id, name, profile }),
      });
      if (!res.ok) { const err = await res.json().catch(() => ({})); throw new Error(err.detail || "failed"); }
      setAuto(await res.json());
      setMsg("");
    } catch (e) {
      setMsg("Automation failed: " + e.message);
    }
    setBusy(false);
  }

  return (
    <div className="actions">
      <input placeholder="Your name (for the PDF and form)" value={name}
             onChange={(e) => setName(e.target.value)} />
      <button onClick={downloadPdf}>Download pre-filled PDF</button>
      <button className="agent" onClick={runAutomation} disabled={busy}>
        {busy ? "Agent is working..." : "Auto-fill demo portal (agent)"}
      </button>
      <div className="remRow">
        <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        <button className="ghost" onClick={saveReminder}>Set reminder</button>
      </div>
      {msg && <small>{msg}</small>}
      {auto && (
        <div className="receipt">
          <strong>Receipt: {auto.receipt_id}</strong>
          <img src={`${API}${auto.screenshot}`} alt="Demo portal receipt" />
        </div>
      )}
    </div>
  );
}



