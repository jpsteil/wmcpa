from reportlab.lib.fonts import addMapping
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
import reportlab.rl_config
import os
import sqlite3


BASE_PATH = os.path.join("/home", "jim", "dev", "py4web", "apps", "wmcpa")
OUTPUT_FILE = os.path.join(BASE_PATH, 'scripts', 'speaker.pdf')
DATABASE_NAME = os.path.join(BASE_PATH, "databases", "storage.db")

#  Report Setup
reportlab.rl_config.warnOnMissingFontGlyphs = 0
pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial Bold", "arialbd.ttf"))
pdfmetrics.registerFont(TTFont("Arial Bold Italic", "arialbi.ttf"))
pdfmetrics.registerFont(TTFont("Arial Italic", "ariali.ttf"))

addMapping("Arial", 0, 0, "Arial")
addMapping("Arial", 0, 1, "Arial Italic")
addMapping("Arial", 1, 0, "Arial Bold")
addMapping("Arial", 1, 1, "Arial Bold Italic")

base_font = "Arial"
bold_font = "Arial Bold"

PAGE_HEIGHT = letter[1]
PAGE_WIDTH = letter[0]

styles = getSampleStyleSheet()
styleN = styles["Normal"]

REPORT_STYLE = TableStyle(
    [
        ("FONTNAME", (0, 0), (-1, -1), base_font),
        ("FONTSIZE", (0, 0), (-1, -1), 12),
        ("ALIGNMENT", (0, 0), (0, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
)


def first_page(canvas, doc):
    canvas.saveState()

    canvas.setFont(bold_font, 22)
    canvas.drawString(0.5 * inch, PAGE_HEIGHT - 1 * inch, f"{doc.first_name} {doc.last_name}")
    canvas.setFont(base_font, 10)
    canvas.drawString(0.5 * inch, PAGE_HEIGHT - 1.2 * inch, doc.title)
    canvas.drawString(0.5 * inch, PAGE_HEIGHT - 1.35 * inch, doc.company)

    canvas.restoreState()


def subsequent_pages(canvas, doc):
    first_page(canvas, doc)


def speaker_profile(speaker_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute(
        "SELECT first_name, last_name, title, company, bio FROM speaker WHERE id = ?",
        [speaker_id],
    )
    first_name = None
    last_name = None
    title = None
    company = None
    bio = None
    for first_name, last_name, title, company, bio in c.fetchall():
        pass

    doc = SimpleDocTemplate(
        OUTPUT_FILE,
        pagesize=letter,
        leftMargin=0.35 * inch,
        topMargin=1.6 * inch,
        rightMargin=0.5 * inch,
        bottomMargin=1.0 * inch,
    )
    doc.first_name = first_name
    doc.last_name = last_name
    doc.title = title
    doc.company = company

    report_story = []
    report_data = [[Paragraph(bio.replace('\n', '<br />'), styleN)]]
    col_widths = [PAGE_WIDTH - .75 * inch]

    data_table = Table(
        data=report_data, hAlign="LEFT", colWidths=col_widths, repeatRows=1
    )
    data_table.setStyle(tblstyle=REPORT_STYLE)
    report_story.append(data_table)

    c.close()
    conn.close()

    doc.build(report_story, onFirstPage=first_page, onLaterPages=subsequent_pages)

    return


if __name__ == "__main__":
    speaker_profile(1)
