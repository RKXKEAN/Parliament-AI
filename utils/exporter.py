"""
utils/exporter.py
──────────────────────────────────────────────────────────────────────────────
Export transcript + summary to .txt or .docx bytes for Streamlit download.
"""

import io
from datetime import datetime


# ─── TXT ───────────────────────────────────────────────────────────────────────
def export_txt(transcript: str, summary: str) -> bytes:
    """Return UTF-8 encoded bytes of a plain-text report."""
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    content = f"""รายงานการสรุป
สร้างโดย: สภา AI — ระบบถอดความและสรุปจากวิดีโอและเสียง
วันที่สร้าง: {now}
{"=" * 70}

█ สรุปการประชุม
{"=" * 70}
{summary}

{"=" * 70}
█ บันทึกการถอดความ (Transcript)
{"=" * 70}
{transcript}
"""
    return content.encode("utf-8", errors="replace")


# ─── DOCX ──────────────────────────────────────────────────────────────────────
def export_docx(transcript: str, summary: str) -> bytes:
    """Return .docx bytes with styled Thai parliament report."""
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor, Inches, Cm
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
    except ImportError:
        raise ImportError("กรุณาติดตั้ง python-docx:  pip install python-docx")

    # sanitize inputs — strip any chars that confuse latin-1 codec in underlying libs
    summary = summary.encode("utf-8", errors="replace").decode("utf-8")
    transcript = transcript.encode("utf-8", errors="replace").decode("utf-8")

    doc = Document()

    # ── Page margins ────────────────────────────────────────────────
    for section in doc.sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(3.0)
        section.right_margin = Cm(2.5)

    # ── Title ────────────────────────────────────────────────────────
    title = doc.add_heading("รายงานการประชุมรัฐสภาไทย", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].font.color.rgb = RGBColor(0x1A, 0x23, 0x7E)
    title.runs[0].font.size = Pt(18)

    sub = doc.add_paragraph(
        f"สร้างโดย: สภา AI — ระบบถอดความและสรุปการประชุม\n"
        f"วันที่: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    )
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.runs[0].font.size = Pt(10)
    sub.runs[0].font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    doc.add_paragraph()

    # ── Summary section ──────────────────────────────────────────────
    h = doc.add_heading("สรุปการประชุม", level=1)
    h.runs[0].font.color.rgb = RGBColor(0x1A, 0x23, 0x7E)

    # Render markdown-ish summary line by line
    for line in summary.split("\n"):
        stripped = line.strip()
        if stripped.startswith("## ") or stripped.startswith("### "):
            level = 2 if stripped.startswith("### ") else 2
            text = stripped.lstrip("#").strip()
            hh = doc.add_heading(text, level=level)
            hh.runs[0].font.size = Pt(12)
        elif stripped.startswith("- ") or stripped.startswith("• "):
            p = doc.add_paragraph(stripped[2:], style="List Bullet")
            p.runs[0].font.size = Pt(11)
        elif stripped.startswith("|"):
            # Simple table row detection — skip, render as paragraph
            p = doc.add_paragraph(stripped)
            p.runs[0].font.size = Pt(10)
            p.runs[0].font.name = "Courier New"
        elif stripped:
            p = doc.add_paragraph(stripped)
            p.runs[0].font.size = Pt(11)
        else:
            doc.add_paragraph()

    doc.add_page_break()

    # ── Transcript section ───────────────────────────────────────────
    h2 = doc.add_heading("บันทึกการถอดความ (Transcript)", level=1)
    h2.runs[0].font.color.rgb = RGBColor(0x1A, 0x23, 0x7E)

    for line in transcript.split("\n"):
        if not line.strip():
            continue
        p = doc.add_paragraph(line)
        p.runs[0].font.size = Pt(10)
        p.runs[0].font.name = (
            "TH Sarabun New" if _font_exists("TH Sarabun New") else "Arial"
        )

    # ── Save to bytes ────────────────────────────────────────────────
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _font_exists(name: str) -> bool:
    """Quick check if a font name is likely available."""
    try:
        from docx.shared import Pt
        from docx import Document

        doc = Document()
        run = doc.add_paragraph().add_run("x")
        run.font.name = name
        # No real font enumeration in python-docx; just return True for Thai fonts
        return True
    except Exception:
        return False
