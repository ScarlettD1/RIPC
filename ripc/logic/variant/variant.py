from time import time
import PyPDF2

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from ripc.logic.required import region_resp_required
from ripc.models import Variant
from ripc.serializers import VariantSerializer


@csrf_exempt
@xframe_options_exempt
@login_required(login_url='/accounts/login/')
@region_resp_required(login_url='/accounts/login/')
def variant_api_file(request, id=0):
    if request.method == "GET":
        if id:
            variants = Variant.objects.get(id=id)
            variants_serializer = VariantSerializer(variants, many=False)
            file_path = variants_serializer['file_path'].value
            file_name = file_path.split('&&')[-1]
            return FileResponse(open(file_path, "rb"), as_attachment=False, filename=file_name)

    return JsonResponse("ERROR", status=400, safe=False)


@csrf_exempt
@login_required(login_url='/accounts/login/')
@region_resp_required(login_url='/accounts/login/')
def variant_api(request):
    if request.method == "POST" and request.GET.get('update'):
        variant_ids = []
        for name, file in request.FILES.items():
            var_id = name.split('&&')[0]
            old_variant = Variant.objects.get(id=var_id)

            filename = name.split('&&')[1]
            file_path = f'File_Storage/variant/{int(time())}&&{filename}'
            with open(file_path, "wb") as new_file:
                new_file.write(file.read())
            # Считываем PDF для подсчёта страниц
            reader = PyPDF2.PdfReader(file_path)
            data = {"page_count": str(len(reader.pages)), "file_path": file_path, "event": old_variant.event_id}

            variants_serializer = VariantSerializer(old_variant, data=data)
            if not variants_serializer.is_valid():
                print(variants_serializer.errors)
                return JsonResponse("ERROR", status=400, safe=False)
            variants_serializer.save()
            variant_ids.append(var_id)
        return JsonResponse(variant_ids, status=200, safe=False)

    if request.method == "POST":
        datas = []
        event_id = request.POST['event_id']
        for name, file in request.FILES.items():
            file_path = f'File_Storage/variant/{int(time())}&&{name}'
            with open(file_path, "wb") as new_file:
                new_file.write(file.read())
            # Считываем PDF для подсчёта страниц
            reader = PyPDF2.PdfReader(file_path)
            datas.append({"page_count": str(len(reader.pages)), "file_path": file_path, "event": event_id})

        variant_ids = []
        for data in datas:
            variants_serializer = VariantSerializer(data=data)
            if not variants_serializer.is_valid():
                return JsonResponse("ERROR", status=400, safe=False)
            variants_serializer.save()
            variant_ids.append(variants_serializer.data.get('id'))
        return JsonResponse(variant_ids, status=200, safe=False)

    if request.method == "GET":
        query = {}
        # Поиск query
        ids = request.GET.get('id')
        if ids and len(ids.split(',')) > 1:
            ids = ids.split(',')

        if ids:
            query['id__in'] = ids if type(ids) is list else [ids]

        if query:
            patterns = Variant.objects.filter(**query)
            patterns_serializer = VariantSerializer(patterns, many=True)
            return JsonResponse(patterns_serializer.data, status=200, safe=False)

    return JsonResponse("ERROR", status=400, safe=False)
