import { useState } from "react";
import "./App.css";
import Actions, { Reminders } from "./Actions";
import VoiceBar, { speak } from "./Voice";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8001";

const T = {
  en: {
    sub: "Find government schemes you are eligible for",
    ph: "Example: I am 19, female, SC, family income 2 lakhs, studying degree",
    send: "Send",
    hello: "Tell me about yourself: age, family income, category (SC/ST/BC/OC), student or farmer, male or female.",
    found: (n) => `I found ${n} scheme${n === 1 ? "" : "s"} for you.`,
    why: "Why you qualify", docs: "Documents needed", where: "Where to get",
    apply: "Official website", reset: "Start over", profile: "Your details",
    err: "Cannot reach the server. Is the backend running?",
  },
  te: {
    sub: "Meeku eligible ayye government schemes kanugonandi",
    ph: "Udaharana: Nenu 19 ella ammayini, SC, intlo income 2 lakhs, degree chaduvutunna",
    send: "Pampu",
    hello: "Mee gurinchi cheppandi: vayasu, income, category (SC/ST/BC/OC), student leka raithu, abbayi leka ammayi.",
    found: (n) => `Meeku ${n} schemes dorikayi.`,
    why: "Meeru enduku eligible", docs: "Kavalsina documents", where: "Ekkada teesukovali",
    apply: "Official website", reset: "Malli modalu", profile: "Mee vivaralu",
    err: "Server dorakatledu. Backend run avtunda?",
  },
  hi: {
    sub: "Aap jin sarkari yojanaon ke yogya hain unhe khojiye",
    ph: "Udaharan: Main 19 saal ki ladki hoon, SC, parivar ki aay 2 lakh, degree padh rahi hoon",
    send: "Bhejein",
    hello: "Apne baare mein bataiye: umar, aay, category (SC/ST/BC/OC), student ya kisan, ladka ya ladki.",
    found: (n) => `Aapke liye ${n} yojanayein mili.`,
    why: "Aap kyon yogya hain", docs: "Zaroori documents", where: "Kahan se milenge",
    apply: "Official website", reset: "Dobara shuru karein", profile: "Aapki jaankari",
    err: "Server se connect nahi ho paaya. Kya backend chal raha hai?",
  },
};

export default function App() {
  const [lang, setLang] = useState("en");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [profile, setProfile] = useState({});
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [docs, setDocs] = useState({});
  const [open, setOpen] = useState(null);
  const [voiceOn, setVoiceOn] = useState(false);
  const t = T[lang];

  async function send(textOverride) {
    const msg = (typeof textOverride === "string" ? textOverride : input).trim();
    if (!msg || loading) return;
    setMessages((m) => [...m, { from: "user", text: msg }]);
    setInput("");
    setLoading(true);
    try {
      const res = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg, language: lang, profile }),
      });
      const data = await res.json();
      setProfile(data.profile);
      setMatches(data.matches);
      const reply = [data.count > 0 ? t.found(data.count) : "", data.question]
        .filter(Boolean).join(" ");
      setMessages((m) => [...m, { from: "bot", text: reply }]);
      if (voiceOn && reply) speak(reply);
    } catch (e) {
      setMessages((m) => [...m, { from: "bot", text: t.err }]);
    }
    setLoading(false);
  }

  async function toggle(id) {
    if (open === id) { setOpen(null); return; }
    setOpen(id);
    if (!docs[id]) {
      try {
        const r = await fetch(`${API}/schemes/${id}/documents`);
        const d = await r.json();
        setDocs((x) => ({ ...x, [id]: d.documents }));
      } catch (e) {}
    }
  }

  function reset() {
    setMessages([]); setProfile({}); setMatches([]); setOpen(null); setInput("");
  }

  return (
    <div className="app">
      <header>
        <div>
          <h1>SchemeSaathi</h1>
          <p>{t.sub}</p>
        </div>
        <select value={lang} onChange={(e) => setLang(e.target.value)}>
          <option value="en">English</option>
          <option value="te">Telugu</option>
          <option value="hi">Hindi</option>
        </select>
      </header>

      <div className="chat">
        <div className="bubble bot">{t.hello}</div>
        {messages.map((m, i) => (
          <div key={i} className={`bubble ${m.from}`}>{m.text}</div>
        ))}
        {loading && <div className="bubble bot">...</div>}
      </div>

      <div className="inputRow">
        <input
          value={input}
          placeholder={t.ph}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
        />
        <button onClick={send}>{t.send}</button>
        <button className="ghost" onClick={reset}>{t.reset}</button>
      </div>

      <VoiceBar lang={lang} onText={(txt) => { setInput(txt); send(txt); }} voiceOn={voiceOn} setVoiceOn={setVoiceOn} />
      {Object.keys(profile).length > 0 && (
        <div className="profile">
          <strong>{t.profile}: </strong>
          {Object.entries(profile).map(([k, v]) => (
            <span key={k} className="chip">{k}: {String(v)}</span>
          ))}
        </div>
      )}

      <div className="cards">
        {matches.map((s) => (
          <div key={s.id} className="card">
            <h3>{s.name}</h3>
            <p className="benefit">{s.benefit}</p>
            <p className="why"><strong>{t.why}:</strong></p>
            <ul>{s.why_you_qualify.map((r, i) => <li key={i}>{r}</li>)}</ul>
            <button onClick={() => toggle(s.id)}>{t.docs}</button>
            {open === s.id && docs[s.id] && (
              <ul className="docs">
                {docs[s.id].map((d, i) => (
                  <li key={i}>
                    <input type="checkbox" /> {d.name}
                    <span className="where"> ({t.where}: {d.where_to_get})</span>
                  </li>
                ))}
              </ul>
            )}
            <Actions scheme={s} profile={profile} />
            <a href={s.official_link} target="_blank" rel="noreferrer">{t.apply}</a>
          </div>
        ))}
      </div>

      <Reminders />
      {matches.length > 0 && (
        <p className="disclaimer">Verify details on the official website before applying.</p>
      )}
    </div>
  );
}




