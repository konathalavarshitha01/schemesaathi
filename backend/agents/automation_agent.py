import json
import os
import sys
from playwright.sync_api import sync_playwright

def main():
    cfg = json.loads(sys.argv[1])
    p = cfg["profile"]
    headless = os.environ.get("HEADLESS", "0") == "1"
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=headless, slow_mo=500)
        page = browser.new_page(viewport={"width": 900, "height": 900})
        page.goto(cfg["base"] + "/demo-portal")
        page.fill("#name", cfg["name"] or "Demo Applicant")
        page.fill("#age", str(p.get("age") or ""))
        page.select_option("#gender", p.get("gender") or "female")
        page.select_option("#category", (p.get("category") or "SC").upper())
        page.fill("#income", str(p.get("income") or ""))
        page.fill("#scheme", cfg["scheme_name"])
        page.check("#declare")
        page.click("#submit")
        page.wait_for_selector("#receipt-id")
        receipt = page.inner_text("#receipt-id")
        page.screenshot(path=cfg["out"])
        page.wait_for_timeout(1500)
        browser.close()
    print(receipt)

main()
