import { useState, useRef } from "react";

const SR = typeof window !== "undefined" &&
  (window.SpeechRecognition || window.webkitSpeechRecognition);
const LOCALE = { en: "en-IN", te: "te-IN", hi: "hi-IN" };

export function speak(text) {
  if (!("speechSynthesis" in window) || !text) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = "en-IN";
  window.speechSynthesis.speak(u);
}

export default function VoiceBar({ lang, onText, voiceOn, setVoiceOn }) {
  const [listening, setListening] = useState(false);
  const [note, setNote] = useState("");
  const ref = useRef(null);

  function start() {
    if (!SR) { setNote("Voice input needs Chrome or Edge."); return; }
    const r = new SR();
    r.lang = LOCALE[lang] || "en-IN";
    r.interimResults = false;
    r.maxAlternatives = 1;
    r.onstart = () => { setListening(true); setNote(""); };
    r.onresult = (e) => onText(e.results[0][0].transcript);
    r.onerror = (e) => setNote("Mic error: " + e.error);
    r.onend = () => setListening(false);
    ref.current = r;
    r.start();
  }

  function stop() { if (ref.current) ref.current.stop(); }

  return (
    <div className="voiceBar">
      <button className={listening ? "mic on" : "mic"} onClick={listening ? stop : start}>
        {listening ? "Listening... tap to stop" : "Speak"}
      </button>
      <label>
        <input type="checkbox" checked={voiceOn}
               onChange={(e) => setVoiceOn(e.target.checked)} /> Read replies aloud
      </label>
      {note && <small>{note}</small>}
    </div>
  );
}
