from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from ripc.logic.required import region_rep_required
from ripc.models import VariantCropping
from ripc.serializers import VariantCroppingSerializer


@csrf_exempt
@login_required(login_url='/accounts/login/')
@region_rep_required(login_url='/accounts/login/')
def start_cropping_variant(request, id=0):
    if request.method == "GET":
        if id:
            result_ids = []
            # Старт функции обрезки
            result = [{"task_file_path": "File_Storage/task/1.png", "answer_coord": [0, 0, 1, 1]},
                      {"task_file_path": "File_Storage/task/2.png", "answer_coord": [0, 0, 1, 1]},
                      {"task_file_path": "File_Storage/task/3.png", "answer_coord": [0, 0, 1, 1]}]

            # Сохранение результата
            for data in result:
                variant_cropping_serializer = VariantCroppingSerializer(data=data)
                if not variant_cropping_serializer.is_valid():
                    return JsonResponse("ERROR", status=400, safe=False)
                variant_cropping_serializer.save()
                result_ids.append(variant_cropping_serializer.data.get('id'))
            return JsonResponse(result_ids, status=200, safe=False)
    return JsonResponse("ERROR", status=400, safe=False)


@csrf_exempt
@login_required(login_url='/accounts/login/')
def cropping_variant_image(request, id=0):
    if request.method == "GET":
        if id:
            cropping = VariantCropping.objects.get(id=id)
            cropping_serializer = VariantCroppingSerializer(cropping, many=False)
            with open(cropping_serializer.data.get('task_file_path'), "rb") as f:
                return HttpResponse(f.read(), content_type="image/png")

    return JsonResponse("ERROR", status=400, safe=False)