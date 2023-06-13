from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from ripc.logic.required import region_resp_required
from ripc.models import Variant, Criteria, CriteriaCropping, VariantCropping, PatternTask
from ripc.serializers import TaskSerializer

@csrf_exempt
@login_required(login_url='/accounts/login/')
@region_resp_required(login_url='/accounts/login/')
def task_api(request):
    if request.method == "GET" and request.GET.get('end_step'):
        event_id = request.GET.get('event')
        datas = []
        task_ids = []

        pattern_tasks = PatternTask.objects.filter(event=event_id)
        variants = Variant.objects.filter(event=event_id)
        for variant in variants:
            criteria = Criteria.objects.filter(variant=variant.id).first()
            criteria_cropping_list = CriteriaCropping.objects.filter(criteria=criteria.id)
            for criteria_cropping in criteria_cropping_list:
                task_num = criteria_cropping.task_num
                pattern_task = pattern_tasks.filter(task_num=task_num).first()
                variant_cropping = VariantCropping.objects.filter(variant=variant.id, task_num=task_num).first()
                datas.append({
                    "pattern": pattern_task.id,
                    "variant": variant.id,
                    "criteria_cropping": criteria_cropping.id,
                    "variant_cropping": variant_cropping.id,
                    "task_num": task_num
                })

        for data in datas:
            task_serializer = TaskSerializer(data=data)
            if not task_serializer.is_valid():
                return JsonResponse("ERROR", status=500, safe=False)

            task_serializer.save()
            task_ids.append(task_serializer.data.get('id'))
        return JsonResponse(task_ids, status=200, safe=False)

    if request.method == "POST":
        datas = []
        task_ids = []
        task_data = JSONParser().parse(request)
        if type(task_data) is dict:
            datas.append(task_data)
        else:
            datas = task_data

        for data in datas:
            task_serializer = TaskSerializer(data=data)
            if not task_serializer.is_valid():
                return JsonResponse("ERROR", status=500, safe=False)

            task_serializer.save()
            task_ids.append(task_serializer.data.get('id'))
        return JsonResponse(task_ids, status=200, safe=False)