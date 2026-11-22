import textwrap
from io import BytesIO
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def build_pdf(scheme, profile, applicant_name=""):
    """Builds a pre-filled application summary PDF (a draft, not an official form)."""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    _, h = A4
    y = h - 60

    def line(text, font="Helvetica", size=11, gap=16):
        nonlocal y
        c.setFont(font, size)
        for part in textwrap.wrap(str(text), 90) or [""]:
            c.drawString(50, y, part)
            y -= gap

    income = profile.get("income")
    income_text = f"Rs {income:,}" if isinstance(income, int) else "-"

    line("SchemeSaathi - Application Summary", "Helvetica-Bold", 16, 26)
    line(f"Generated on: {date.today().isoformat()}", size=9)
    line("DRAFT for your reference. Not an official government form.", "Helvetica-Oblique", 9, 24)

    line("Applicant details", "Helvetica-Bold", 13, 20)
    line(f"Name: {applicant_name or '____________________'}")
    line(f"Age: {profile.get('age', '-')}")
    line(f"Gender: {profile.get('gender', '-')}")
    line(f"Category: {profile.get('category', '-')}")
    line(f"Occupation: {profile.get('occupation', '-')}")
    line(f"Annual family income: {income_text}", gap=24)

    line("Scheme", "Helvetica-Bold", 13, 20)
    line(f"Name: {scheme['name']}")
    line(f"Benefit: {scheme['benefit']}")
    line(f"Official website: {scheme['official_link']}", gap=24)

    line("Documents checklist", "Helvetica-Bold", 13, 20)
    for d in scheme["documents"]:
        line(f"[  ] {d['name']}  (Where to get: {d['where_to_get']})")
    y -= 10

    line("Verify all details on the official website before applying.", "Helvetica-Oblique", 9)
    c.save()
    return buf.getvalue()
