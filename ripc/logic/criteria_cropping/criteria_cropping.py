from time import time

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from ripc.logic.required import region_resp_required
from ripc.models import CriteriaCropping
from ripc.serializers import CriteriaCroppingSerializer


@csrf_exempt
@login_required(login_url='/accounts/login/')
@region_resp_required(login_url='/accounts/login/')
def start_cropping_criteria(request, id=0):
    if request.method == "GET":
        if id:
            result_ids = []

            # Старт функции обрезки критериев
            result = [{"criteria": id, "file_path": f"File_Storage\criteria\\{int(time())}&&{id}_1.png", "task_num": 1},
                      {"criteria": id, "file_path": f"File_Storage\criteria\\{int(time())}&&{id}_2.png", "task_num": 2},
                      {"criteria": id, "file_path": f"File_Storage\criteria\\{int(time())}&&{id}_3.png", "task_num": 3}]

            # Удаление старых данных
            if request.GET["update"]:
                CriteriaCropping.objects.filter(variant=id).delete()

            # Сохранение результата
            for data in result:
                criteria_cropping_serializer = CriteriaCroppingSerializer(data=data)
                if not criteria_cropping_serializer.is_valid():
                    return JsonResponse("ERROR", status=400, safe=False)
                criteria_cropping_serializer.save()
                result_ids.append(criteria_cropping_serializer.data.get('id'))
            return JsonResponse(result_ids, status=200, safe=False)
    return JsonResponse("ERROR", status=400, safe=False)


@csrf_exempt
@login_required(login_url='/accounts/login/')
def cropping_criteria_image(request, id=0):
    if request.method == "GET":
        if id:
            cropping = CriteriaCropping.objects.get(id=id)
            cropping_serializer = CriteriaCroppingSerializer(cropping, many=False)
            with open(cropping_serializer.data.get('file_path'), "rb") as f:
                return HttpResponse(f.read(), content_type="image/png")

    return JsonResponse("ERROR", status=400, safe=False)