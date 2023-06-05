import io
import os

from django.conf import settings
from django.db.models import QuerySet
from django.http import FileResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def pdf_cart(ingredients: QuerySet) -> FileResponse:
    """Создание pdf со списком покупок."""

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    font = os.path.join(settings.FONTS_DIR, 'freesansbold.ttf')
    pdfmetrics.registerFont(TTFont('FreeSans', font))
    pdf.setFont('FreeSans', 24)
    pdf.drawString(100, 800, 'Список покупок')
    pdf.line(40, 790, 560, 790)
    pdf.setFontSize(14)
    y_coord = 700
    for ingredient in ingredients:
        if y_coord < 70:
            pdf.showPage()
            pdf.setFont('FreeSans', 14)
            pdf.drawString(50, 800, 'продолжение списка покупок')
            pdf.line(40, 790, 560, 790)
            y_coord = 700
        name = ingredient.get('ingredient__name')
        measurement_unit = ingredient.get('ingredient__measurement_unit')
        amount = ingredient.get('amount')
        string = f'{name},  {amount} {measurement_unit}'
        pdf.drawString(30, y_coord, string)
        y_coord -= 40
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return FileResponse(
        buffer, as_attachment=True, filename='shopping_list.pdf'
    )
