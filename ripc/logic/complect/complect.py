import math
import tempfile

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from docx.shared import Inches, Pt, Cm

from ripc.models import Complect
from ripc.serializers import ComplectSerializer

from docx import Document


@csrf_exempt
@xframe_options_exempt
@login_required(login_url='/accounts/login/')
def complects_id_file(request, event_id=0):
    if request.method == "GET":
        # Поиск query
        organization_id = request.GET.get('organization_id')

        complects = Complect.objects.filter(event=event_id, organization=organization_id)
        complects_serializer = ComplectSerializer(complects, many=True)
        complects_data = complects_serializer.data

        # Создание таблицы в DOCX файле
        document = Document()
        style = document.styles['Normal']
        font = style.font
        font.name = 'Times New Roman'
        font.size = Pt(12)
        count_rows = math.ceil(len(complects_data) / 2)
        table = document.add_table(rows=count_rows, cols=4)
        table.style = 'Table Grid'
        table.autofit = False

        row = table.rows[0].cells
        row[0].text = 'Номер комплекта'
        row[1].text = 'ФИО'
        row[2].text = 'Номер комплекта'
        row[3].text = 'ФИО'

        row[0].width = Cm(2)
        row[1].width = Cm(5)
        row[2].width = Cm(2)
        row[3].width = Cm(5)

        for i in range(0, len(complects_data), 2):
            row = table.add_row().cells
            row[0].text = str(complects_data[i]['id'])
            row[2].text = str(complects_data[i+1]['id'])

        for row in table.rows:
            row.height = Cm(0.7)

        # Сохранение DOCX
        tf = tempfile.NamedTemporaryFile(suffix='.docx', delete=False)
        file_path = tf.name
        document.save(file_path)
        return FileResponse(open(file_path, "rb"), as_attachment=False, filename=f"Таблица компектов {event_id}.docx")

    return JsonResponse("ERROR", status=400, safe=False)