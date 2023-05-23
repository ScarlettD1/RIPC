from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from ripc.logic.required import region_rep_required
from ripc.models import PatternTask
from ripc.serializers import PatternTaskSerializer


@csrf_exempt
@login_required(login_url='/accounts/login/')
@region_rep_required(login_url='/accounts/login/')
def pattern_api(request):
    if request.method == "GET":
        query = {}
        # Поиск query
        ids = request.GET.get('id')
        if ids and len(ids.split(',')) > 1:
            ids = ids.split(',')

        if ids:
            query['id__in'] = ids if type(ids) is list else [ids]

        if query:
            patterns = PatternTask.objects.filter(**query)
            patterns_serializer = PatternTaskSerializer(patterns, many=True)
            return JsonResponse(patterns_serializer.data, status=200, safe=False)

        # Если query нет
        patterns = PatternTask.objects.all()
        patterns_serializer = PatternTaskSerializer(patterns, many=True)
        return JsonResponse(patterns_serializer.data, status=200, safe=False)

    if request.method == "POST":
        datas = []
        pattern_ids = []
        pattern_data = JSONParser().parse(request)
        if type(pattern_data) is dict:
            datas.append(pattern_data)
        else:
            datas = pattern_data
        for data in datas:
            pattern_serializer = PatternTaskSerializer(data=data)
            if not pattern_serializer.is_valid():
                print(pattern_serializer.errors)
                return JsonResponse("ERROR", status=500, safe=False)
            pattern_serializer.save()
            pattern_ids.append(pattern_serializer.data.get('id'))
        return JsonResponse(pattern_ids, status=200, safe=False)
