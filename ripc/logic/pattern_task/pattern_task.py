from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from ripc.models import Subject
from ripc.serializers import PatternTaskSerializer

@csrf_exempt
@login_required(login_url='/accounts/login/')
def pattern_api_get(request, id=0):
    if request.method == "GET":
        if id:
            patterns = Subject.objects.get(id=id)
            patterns_serializer = PatternTaskSerializer(patterns, many=False)
        else:
            patterns = Subject.objects.all()
            patterns_serializer = PatternTaskSerializer(patterns, many=True)

        return JsonResponse(patterns_serializer.data, status=200, safe=False)


@csrf_exempt
@login_required(login_url='/accounts/login/')
def pattern_api_post(request):
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