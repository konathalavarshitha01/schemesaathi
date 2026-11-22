import json
import os
import uuid

PATH = "data/reminders.json"

def _load():
    if not os.path.exists(PATH):
        return []
    with open(PATH, encoding="utf-8-sig") as f:
        return json.load(f)

def add_reminder(scheme_id, scheme_name, date, note=""):
    items = _load()
    item = {"id": uuid.uuid4().hex[:8], "scheme_id": scheme_id,
            "scheme_name": scheme_name, "date": date, "note": note}
    items.append(item)
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)
    return item

def list_reminders():
    return sorted(_load(), key=lambda r: r["date"])
