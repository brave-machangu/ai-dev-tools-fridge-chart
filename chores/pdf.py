"""The fridge chart: one printable page for the coming week."""

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

GRID = TableStyle([
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('LINEBELOW', (0, 0), (-1, 0), 0.75, colors.black),
    ('LINEBELOW', (0, 1), (-1, -2), 0.25, colors.lightgrey),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
])


def build_week_chart(family, week_start, rows, bounties):
    """Render the week to PDF bytes: rotation per child, balances, bounties.

    ``rows`` is the same structure the dashboard uses -- one entry per child
    with their assignments and current balance -- so the printout and the
    screen cannot disagree.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        title=f'{family.name} - week of {week_start}',
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=1.8 * cm, bottomMargin=1.8 * cm,
    )
    styles = getSampleStyleSheet()
    story = [
        Paragraph(family.name, styles['Title']),
        Paragraph(f'Week of {week_start:%d %B %Y}', styles['Heading3']),
        Spacer(1, 0.5 * cm),
    ]

    for row in rows:
        child = row['child']
        heading = Paragraph(
            f"{child.display_name} &mdash; {row['balance']} points",
            styles['Heading2'],
        )
        if row['assignments']:
            data = [['Chore', 'Points', 'Done?']]
            for assignment in row['assignments']:
                data.append([
                    assignment.chore.title,
                    str(assignment.chore.points),
                    'approved' if assignment.is_approved else '',
                ])
        else:
            data = [['Chore', 'Points', 'Done?'], ['Nothing assigned', '', '']]

        table = Table(data, colWidths=[9 * cm, 2.5 * cm, 4.5 * cm])
        table.setStyle(GRID)
        story.append(KeepTogether([heading, table, Spacer(1, 0.4 * cm)]))

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph('Bounty board', styles['Heading2']))
    if bounties:
        data = [['Bounty', 'Points', 'Claimed by']]
        for bounty in bounties:
            assignment = bounty.assignments.first()
            data.append([
                bounty.title,
                str(bounty.points),
                assignment.child.display_name if assignment else 'unclaimed',
            ])
        table = Table(data, colWidths=[9 * cm, 2.5 * cm, 4.5 * cm])
        table.setStyle(GRID)
        story.append(table)
    else:
        story.append(Paragraph('No bounties posted.', styles['Normal']))

    doc.build(story)
    return buffer.getvalue()
