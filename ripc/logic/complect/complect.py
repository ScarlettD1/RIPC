import io
import math

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from docx.shared import Inches, Pt, Cm
from rest_framework.parsers import JSONParser

from ripc.logic.required import some_resp_required
from ripc.models import Complect, OrganizationRep, OrganizationEvent
from ripc.serializers import ComplectSerializer, OrganizationEventSerializer

from docx import Document
from zipfile import ZipFile


@csrf_exempt
@xframe_options_exempt
@login_required(login_url='/accounts/login/')
@some_resp_required(login_url='/accounts/login/')
def complects_download(request, event_id=0):
    if request.method == "GET":
        # Поиск id организации
        organization_id = request.GET.get('organization_id')
        if not organization_id:
            user_org = OrganizationRep.objects.filter(user=request.user.id).first()
            organization_id = user_org.organization_id

        # Получаем имформацию об организации в МП
        event_organizations = OrganizationEvent.objects.filter(event=event_id, organization=organization_id)[0]
        event_organizations_serializer = OrganizationEventSerializer(event_organizations, many=False)
        event_organizations_data = event_organizations_serializer.data

        complects = Complect.objects.filter(organization_event=event_organizations_data['id'])
        complects_serializer = ComplectSerializer(complects, many=True)
        complects_data = complects_serializer.data

        # Создание таблицы "Комплект-ФИО" в DOCX файле
        document = Document()
        style = document.styles['Normal']
        font = style.font
        font.name = 'Times New Roman'
        font.size = Pt(12)
        count_rows = math.ceil(len(complects_data) / 2) - 2
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

        for i in range(0, len(complects_data) - 1, 2):
            row = table.add_row().cells
            row[0].text = str(complects_data[i]['id'])
            row[2].text = str(complects_data[i + 1]['id'])

        for row in table.rows:
            row.height = Cm(0.7)

        docx_io = io.BytesIO()
        document.save(docx_io)

        zip_io = io.BytesIO()
        zip = ZipFile(zip_io, "w")

        # Сохранение DOCX
        zip.writestr(f'_Сопоставление {event_id}.docx', docx_io.getvalue())

        # Сохранение комплектов
        for compect in complects_data:
            zip.writestr(f'{compect["id"]}.pdf', compect["file_path"])
        zip.close()
        zip_io.name = f'Комплекты {event_id}.zip'

        return HttpResponse(zip_io.getvalue(), content_type="application/x-zip-compressed", headers={
            'Content-Disposition': f'attachment;filename=Комплекты {event_id}.zip'
        })

    return JsonResponse("ERROR", status=400, safe=False)


@csrf_exempt
@xframe_options_exempt
@login_required(login_url='/accounts/login/')
@some_resp_required(login_url='/accounts/login/')
def complects_generate(request, event_id=0):
    if request.method == "POST":
        settings_data = JSONParser().parse(request)

        event_id = settings_data.get('event')
        organization_id = settings_data.get('organization')
        count_main = int(settings_data.get('count_main'))
        count_additional = int(settings_data.get('count_additional'))
        event_organization = OrganizationEvent.objects.filter(event=event_id, organization=organization_id)[0]

        # Запуск генерации комплектов (Сёма)
        result = []
        for i in range(count_main):
            result.append({
                "organization_event": event_organization.id,
                "variant": 1,
                "file_path": f"File_Storage\complect\\{i + 1}.pdf",
                "is_additional": False
            })
        for i in range(count_additional):
            result.append({
                "organization_event": event_organization.id,
                "variant": 1,
                "file_path": f"File_Storage\complect\\add_{i + 1}.pdf",
                "is_additional": True
            })

        complects_serializer = ComplectSerializer(data=result, many=True)
        if not complects_serializer.is_valid():
            print(complects_serializer.errors)
            return JsonResponse("ERROR VALID", status=400, safe=False)
        complects_serializer.save()
        return JsonResponse("OK", status=200, safe=False)
    return JsonResponse("ERROR", status=400, safe=False)
