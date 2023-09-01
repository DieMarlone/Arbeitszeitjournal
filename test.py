import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Benutzerdaten
name = "Max Mustermann"
plz = "12345"
stadt = "Musterstadt"

# Arbeitszeitdaten
arbeitsstunden = [
    ["Date", "Start", "End", "Over_hours", "Pause", "Extra_minutes"],
    ["01.09.2023", "08:00", "17:30", "01:00", "30", "0"],
    # Weitere Daten hier hinzufügen
]

# Erstelle ein PDF-Dokument
pdf_filename = "Arbeitszeitjournal.pdf"
doc = SimpleDocTemplate(pdf_filename, pagesize=letter)

# Erstelle einen Story-Container für den Inhalt des PDFs
story = []

# Füge Benutzerdaten zum Story-Container hinzu
styles = getSampleStyleSheet()
text = f"Arbeitszeitjournal für {name}\nPLZ: {plz}\nStadt: {stadt}\n\n"
story.append(Paragraph(text, styles["Normal"]))

# Erstelle eine Tabelle für die Arbeitszeitdaten
data = [arbeitsstunden[0]]  # Überschrift hinzufügen
data.extend(arbeitsstunden[1:])  # Arbeitszeitdaten hinzufügen

table = Table(data, colWidths=[100, 100, 100, 100, 100, 100])
table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                          ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                          ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                          ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                          ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                          ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                          ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

story.append(table)

# Erstelle das PDF-Dokument mit dem Inhalt aus dem Story-Container
doc.build(story)

print(f"Das Arbeitszeitjournal wurde als '{pdf_filename}' gespeichert.")
