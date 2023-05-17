from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from ripc.logic.required import region_rep_required
from ripc.serializers import TaskSerializer


@csrf_exempt
@login_required(login_url='/accounts/login/')
@region_rep_required(login_url='/accounts/login/')
def task_api(request):
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