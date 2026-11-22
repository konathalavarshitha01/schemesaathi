import json
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SchemeSaathi")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

def load_schemes():
    with open("data/schemes.json", encoding="utf-8-sig") as f:
        return json.load(f)

def check_scheme(scheme, age, income, category, occupation, gender):
    """Rule-based matching, so the demo never hallucinates."""
    e = scheme["eligibility"]
    reasons = []

    if age is not None:
        if e["min_age"] is not None and age < e["min_age"]:
            return False, []
        if e["max_age"] is not None and age > e["max_age"]:
            return False, []
        if e["min_age"] is not None or e["max_age"] is not None:
            reasons.append("Your age fits the allowed range")

    if e["max_income"] is not None and income is not None:
        if income > e["max_income"]:
            return False, []
        reasons.append(f"Your family income is within Rs {e['max_income']:,}")

    if e["castes"]:
        if category is None or category.upper() not in e["castes"]:
            return False, []
        reasons.append(f"Open to {category.upper()} category")

    if e["occupations"]:
        if occupation is None or occupation.lower() not in e["occupations"]:
            return False, []
        reasons.append(f"For {occupation.lower()}s")

    if e["gender"]:
        if gender is None or gender.lower() != e["gender"]:
            return False, []
        reasons.append("Meant for women and girls")

    return True, reasons

@app.get("/")
def health():
    return {"status": "SchemeSaathi running"}

@app.get("/schemes")
def all_schemes():
    return load_schemes()

@app.get("/schemes/match")
def match(age: Optional[int] = None, income: Optional[int] = None,
          category: Optional[str] = None, occupation: Optional[str] = None,
          gender: Optional[str] = None):
    results = []
    for s in load_schemes():
        ok, reasons = check_scheme(s, age, income, category, occupation, gender)
        if ok:
            results.append({**s, "why_you_qualify": reasons})
    results.sort(key=lambda r: len(r["why_you_qualify"]), reverse=True)
    return {"count": len(results), "matches": results,
            "disclaimer": "Verify details on the official website before applying."}

@app.get("/schemes/{scheme_id}/documents")
def documents(scheme_id: str):
    for s in load_schemes():
        if s["id"] == scheme_id:
            return {"scheme": s["name"], "documents": s["documents"]}
    raise HTTPException(status_code=404, detail="Scheme not found")

# ---------- Profile Agent chat endpoint ----------
from pydantic import BaseModel
from agents.profile_agent import extract_profile, missing_fields, follow_up

class ChatIn(BaseModel):
    message: str
    language: str = "en"
    profile: dict = {}

@app.post("/chat")
def chat(body: ChatIn):
    profile = extract_profile(body.message, body.profile)
    missing = missing_fields(profile)
    matches = []
    for s in load_schemes():
        if s.get("state") in ("AP", "TS") and profile.get("state") and s["state"] != profile["state"]:
            continue
        ok, reasons = check_scheme(s, profile.get("age"), profile.get("income"),
                                   profile.get("category"), profile.get("occupation"),
                                   profile.get("gender"))
        if ok and reasons:
            matches.append({"id": s["id"], "name": s["name"], "benefit": s["benefit"],
                            "why_you_qualify": reasons, "official_link": s["official_link"]})
    matches.sort(key=lambda r: len(r["why_you_qualify"]), reverse=True)
    return {"profile": profile, "missing": missing,
            "question": follow_up(missing, body.language),
            "count": len(matches), "matches": matches,
            "disclaimer": "Verify details on the official website before applying."}

# ---------- Form Agent + Reminder Agent ----------
from fastapi import Response
from agents.form_agent import build_pdf
from agents.reminder_agent import add_reminder, list_reminders

class FormIn(BaseModel):
    scheme_id: str
    name: str = ""
    profile: dict = {}

@app.post("/form/generate")
def form_generate(body: FormIn):
    for s in load_schemes():
        if s["id"] == body.scheme_id:
            pdf = build_pdf(s, body.profile, body.name)
            return Response(content=pdf, media_type="application/pdf",
                            headers={"Content-Disposition": f'attachment; filename="{s["id"]}-application.pdf"'})
    raise HTTPException(status_code=404, detail="Scheme not found")

class ReminderIn(BaseModel):
    scheme_id: str
    scheme_name: str
    date: str
    note: str = ""

@app.post("/reminders")
def reminders_add(body: ReminderIn):
    return add_reminder(body.scheme_id, body.scheme_name, body.date, body.note)

@app.get("/reminders")
def reminders_list():
    return list_reminders()

# ---------- Demo portal + Automation Agent ----------
import os
import subprocess
import sys
import uuid
import html as _html
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

os.makedirs("data/receipts", exist_ok=True)
app.mount("/receipts", StaticFiles(directory="data/receipts"), name="receipts")

PORTAL = """<!doctype html><html><head><meta charset="utf-8"><title>Demo Scheme Portal</title>
<style>
body{font-family:Arial,sans-serif;background:#eef2f7;margin:0}
.wrap{max-width:520px;margin:30px auto;background:#fff;padding:24px;border-radius:12px}
.banner{background:#fff3cd;padding:8px;border-radius:6px;font-size:13px;margin-bottom:12px}
label{display:block;margin-top:12px;font-size:14px}
input,select{width:100%;padding:8px;margin-top:4px;box-sizing:border-box}
.chk{display:flex;gap:8px;align-items:center}.chk input{width:auto;margin:0}
button{margin-top:18px;background:#1f4e78;color:#fff;border:0;padding:12px 18px;border-radius:8px;font-size:15px}
</style></head><body><div class="wrap">
<div class="banner">DEMO PORTAL: practice form, not a real government website</div>
<h2>Scheme Application Form</h2>
<form action="/demo-portal/submit" method="get">
<label>Full name</label><input id="name" name="name">
<label>Age</label><input id="age" name="age" type="number">
<label>Gender</label><select id="gender" name="gender"><option value="female">female</option><option value="male">male</option></select>
<label>Category</label><select id="category" name="category"><option>SC</option><option>ST</option><option>BC</option><option>OBC</option><option>OC</option></select>
<label>Annual family income (Rs)</label><input id="income" name="income" type="number">
<label>Scheme</label><input id="scheme" name="scheme">
<label class="chk"><input id="declare" name="declare" type="checkbox" value="yes"> I declare the details are true</label>
<button id="submit" type="submit">Submit application</button>
</form></div></body></html>"""

@app.get("/demo-portal", response_class=HTMLResponse)
def demo_portal():
    return PORTAL

@app.get("/demo-portal/submit", response_class=HTMLResponse)
def demo_portal_submit(name: str = "", age: str = "", gender: str = "",
                       category: str = "", income: str = "", scheme: str = "",
                       declare: str = ""):
    rid = "DEMO-" + uuid.uuid4().hex[:8].upper()
    e = _html.escape
    rows = [("Name", name), ("Age", age), ("Gender", gender), ("Category", category),
            ("Income", income), ("Scheme", scheme)]
    trs = "".join(f"<tr><td style='padding:6px;font-weight:bold'>{k}</td><td style='padding:6px'>{e(v)}</td></tr>" for k, v in rows)
    return (f"<!doctype html><html><body style='font-family:Arial;background:#eef2f7'>"
            f"<div id='receipt' style='max-width:520px;margin:30px auto;background:#fff;padding:24px;border-radius:12px'>"
            f"<div style='background:#fff3cd;padding:8px;border-radius:6px;font-size:13px'>DEMO PORTAL: practice only</div>"
            f"<h2 style='color:#1a7f37'>Application received</h2>"
            f"<p>Reference number: <strong id='receipt-id'>{rid}</strong></p>"
            f"<table>{trs}</table></div></body></html>")

class AutoIn(BaseModel):
    scheme_id: str
    name: str = ""
    profile: dict = {}

@app.post("/automation/run")
def automation_run(body: AutoIn, request: Request):
    scheme = next((s for s in load_schemes() if s["id"] == body.scheme_id), None)
    if scheme is None:
        raise HTTPException(status_code=404, detail="Scheme not found")
    shot = uuid.uuid4().hex[:8] + ".png"
    payload = json.dumps({"base": str(request.base_url).rstrip("/"),
                          "scheme_name": scheme["name"], "name": body.name,
                          "profile": body.profile,
                          "out": os.path.join("data", "receipts", shot)})
    try:
        r = subprocess.run([sys.executable, os.path.join("agents", "automation_agent.py"), payload],
                           capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Automation timed out")
    if r.returncode != 0:
        raise HTTPException(status_code=500, detail=r.stderr[-600:])
    receipt = r.stdout.strip().splitlines()[-1]
    return {"receipt_id": receipt, "screenshot": "/receipts/" + shot}


