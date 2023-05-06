import time

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt

from ripc.models import Variant
from ripc.serializers import VariantSerializer


@csrf_exempt
@login_required(login_url='/accounts/login/')
def variant_api_file(request, id=0):
    if request.method == "GET":
        if id:
            variants = Variant.objects.get(id=id)
            variants_serializer = VariantSerializer(variants, many=False)
            file_path = variants_serializer['file_path'].value
            file_name = file_path.split('&&')[-1]
            return FileResponse(open(file_path, "rb"), as_attachment=True, filename=file_name)

    return JsonResponse("ERROR", status=400, safe=False)


@csrf_exempt
@login_required(login_url='/accounts/login/')
def variant_api(request):
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
                return JsonResponse("ERROR", status=400, safe=False)
            variants_serializer.save()
            variant_ids.append(variants_serializer.data.get('id'))
        return JsonResponse(variant_ids, status=200, safe=False)

    return JsonResponse("ERROR", status=400, safe=False)
