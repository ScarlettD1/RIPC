import io
import os
import tempfile
from time import time

import PyPDF2
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from ripc.logic.required import some_rep_required
from ripc.models import Complect, Variant, ScannedPage
from ripc.serializers import ComplectSerializer, ScannedPageSerializer


@csrf_exempt
@login_required(login_url='/accounts/login/')
@some_rep_required(login_url='/accounts/login/')
def complect_scan_data(request):
    if request.method == "GET":
        context = {}

        # Поиск query
        organization_id = request.GET.get('organization_id')
        event_id = request.GET.get('event_id')

        # Получаем имформацию о комплетках МП
        complects = Complect.objects.filter(event=event_id, organization=organization_id)
        complects_serializer = ComplectSerializer(data=complects, many=True)
        complects_data = complects_serializer.data

        # Генерируем списки для комплектов
        context['complect'] = {}
        for complect in complects_data:
            complect_id = str(complect['id'])
            variant_id = str(complect['variant'])
            variant_data = Variant.objects.filter(id=variant_id)[0]
            context['complect'][complect_id] = {
                'pages': [[] for i in range(int(variant_data.page_count))],
                'is_additional': complect['is_additional']
            }

        # Получаем имформацию об отсканированных страницах МП
        scanned_pages = ScannedPage.objects.filter(event=event_id, organization=organization_id).order_by('page_number')
        scanned_pages_serializer = ScannedPageSerializer(scanned_pages, many=True)
        scanned_pages_data = scanned_pages_serializer.data

        context['error_scanned_page'] = []
        for page in scanned_pages_data:
            # Поиск нераспознанных страницах
            if not page['complect']:
                context['error_scanned_page'].append(page)
                continue

            # Заполнение распознанных страниц
            complect_id = str(page['complect'])
            context['complect'][complect_id]['pages'][int(page['page_number']) - 1] = page

        return JsonResponse(context, status=200, safe=False)

    return JsonResponse('Not Found', status=400, safe=False)


@csrf_exempt
def file_from_scanner(request):
    if request.method == "POST":
        print(request.headers)
        if request.headers['Token'] != "05fc8a08-b24a-4bbf-a1b2-82b645f26e28":
            return JsonResponse("Access Denied!", status=403, safe=False)

        data = {}
        data['event'] = request.POST['event_id']
        data['organization'] = request.POST['organization_id']
        byte_file = request.FILES['byte_file'].read()

        file_path = f'File_Storage/scanned_page/{int(time())}&&scan_{data["event"]}_{data["organization"]}.pdf'
        with open(file_path, "wb") as new_file:
            new_file.write(byte_file)
        data['file_path'] = file_path

        # Распознование страницы (Сёма)
        data['complect'] = 1  # Заменить на распознанное
        data['page_number'] = 3  # Заменить на распознанное

        scanned_page_serializer = ScannedPageSerializer(data=data, many=False)
        if not scanned_page_serializer.is_valid():
            return JsonResponse("ERROR VALID", status=400, safe=False)
        scanned_page_serializer.save()
        return JsonResponse("OK", status=200, safe=False)

    return JsonResponse("ERROR", status=400, safe=False)

@csrf_exempt
@xframe_options_exempt
@login_required(login_url='/accounts/login/')
def scanned_api_file(request, id=0):
    if request.method == "GET":
        if id:
            page = ScannedPage.objects.get(id=id)
            page_serializer = ScannedPageSerializer(page, many=False)
            file_path = page_serializer['file_path'].value
            file_name = file_path.split('&&')[-1]
            return FileResponse(open(file_path, "rb"), as_attachment=False, filename=file_name)
    return JsonResponse("ERROR", status=400, safe=False)


@csrf_exempt
@xframe_options_exempt
@login_required(login_url='/accounts/login/')
def scanned_api_files(request, id=0):
    if request.method == "GET":
        if id:
            pages = ScannedPage.objects.filter(complect=id).order_by('page_number')
            pages_serializer = ScannedPageSerializer(pages, many=True)
            pages_data = pages_serializer.data
            merger = PyPDF2.PdfMerger()
            for page in pages_data:
                pdf = page['file_path']
                merger.append(pdf)
            tf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            file_path = tf.name
            merger.write(file_path)
            return FileResponse(open(file_path, "rb"), as_attachment=False, filename=f"Комплект {id}.pdf")

    return JsonResponse("ERROR", status=400, safe=False)


@csrf_exempt
@login_required(login_url='/accounts/login/')
@some_rep_required(login_url='/accounts/login/')
def scanned_api(request, id=0):
    if request.method == "PUT":
        request_data = JSONParser().parse(request)
        scanned_page = ScannedPage.objects.get(id=id)

        data = {}
        # Поиск информации из номера бланка (Сёма)
        data['id'] = scanned_page.id
        data['event'] = scanned_page.event.id
        data['organization'] = scanned_page.organization.id
        data['complect'] = 1 # Заменить на распознанное
        data['file_path'] = scanned_page.file_path
        data['page_number'] = 3 # Заменить на распознанное

        scanned_page_serializer = ScannedPageSerializer(scanned_page, data=data)
        if not scanned_page_serializer.is_valid():
            return JsonResponse("ERROR VALID", status=400, safe=False)
        scanned_page_serializer.save()
        return JsonResponse("OK", status=200, safe=False)

    elif request.method == "DELETE":
        page = ScannedPage.objects.get(id=id)
        file_path = page.file_path
        page.delete()
        os.remove(file_path)
        return JsonResponse("OK", status=200, safe=False)

    return JsonResponse("ERROR", status=400, safe=False)