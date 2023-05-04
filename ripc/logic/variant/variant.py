import base64
import time

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from ripc.models import Variant
from ripc.serializers import VariantSerializer


@csrf_exempt
@login_required(login_url='/accounts/login/')
def variant_api_get(request, id=0):
    if request.method == "GET":
        if id:
            variants = Variant.objects.get(id=id)
            variants_serializer = VariantSerializer(variants, many=False)
            binary = variants_serializer['binary_file'].value
            print(type(binary))
            return FileResponse(variants_serializer['binary_file'].value, status=200)
        print()
    return JsonResponse("ERROR", status=400, safe=False)


@csrf_exempt
@login_required(login_url='/accounts/login/')
def variant_api_post(request):
    if request.method == "POST":
        datas = []
        for name, file in request.FILES.items():
            file_path = f'File_Storage/variant/{time.time()}&&{name}'
            with open(file_path, "wb") as new_file:
                new_file.write(file.read())
                datas.append({"file_path": file_path})

        variant_ids = []
        for data in datas:
            variants_serializer = VariantSerializer(data=data)
            if not variants_serializer.is_valid():
                print(len(data["file_path"]))
                print(variants_serializer.errors)
                return JsonResponse("ERROR", status=400, safe=False)
            variants_serializer.save()
            variant_ids.append(variants_serializer.data.get('id'))

        print(variant_ids)
        return JsonResponse(variant_ids, status=200, safe=False)
    return JsonResponse("ERROR", status=400, safe=False)
