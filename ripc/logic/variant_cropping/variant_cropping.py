from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from ripc.logic.required import region_resp_required
from ripc.models import VariantCropping
from ripc.serializers import VariantCroppingSerializer

from cropping import start_cropping


@csrf_exempt
@login_required(login_url='/accounts/login/')
@region_resp_required(login_url='/accounts/login/')
def start_cropping_variant(request, id=0):
    if request.method == "GET":
        file_path = ''
        if id:
            result_ids = start_cropping(file_path)
            result = []
            for variant in result_ids:
                result = [{"variant": id, "answer_coord": variant['answer'], "task_num": variant['task_num']}]

            # Удаление старых данных
            if request.GET.get("update"):
                VariantCropping.objects.filter(variant=id).delete()

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