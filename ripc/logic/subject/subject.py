from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from ripc.logic.required import region_resp_required
from ripc.models import Subject
from ripc.serializers import SubjectSerializer


@csrf_exempt
@login_required(login_url='/accounts/login/')
@region_resp_required(login_url='/accounts/login/')
def subject_api(request):
    if request.method == "GET":
        query = {}
        # Поиск query
        ids = request.GET.get('id')
        if ids and len(ids.split(',')) > 1:
            ids = ids.split(',')

        if ids:
            query['id__in'] = ids

        if query:
            subjects = Subject.objects.filter(**query)
            subjects_serializer = SubjectSerializer(subjects, many=True)
            return JsonResponse(subjects_serializer.data, status=200, safe=False)

        # Если query нет
        subjects = Subject.objects.all()
        subjects_serializer = SubjectSerializer(subjects, many=True)
        return JsonResponse(subjects_serializer.data, status=200, safe=False)

    elif request.method == "POST":
        subject_data = JSONParser().parse(request)
        subjects_serializer = SubjectSerializer(data=subject_data)
        if subjects_serializer.is_valid():
            subjects_serializer.save()
            return JsonResponse("OK", status=200, safe=False)
        return JsonResponse("ERROR", status=400, safe=False)
    # elif request.method == "PUT":
    #     subject_data = JSONParser().parse(request)
    #     subject = Subject.objects.get(id=subject_data['id'])
    #     subjects_serializer = SubjectSerializer(subject, data=subject_data)
    #     if subjects_serializer.is_valid():
    #         subjects_serializer.save()
    #         return JsonResponse("OK", status=200, safe=False)
    #     return JsonResponse("ERROR", status=400, safe=False)
    # elif request.method == "DELETE":
    #     ids = request.GET.get('id')
    #     subject = Subject.objects.get(id=ids)
    #     subject.delete()
    #     return JsonResponse("ERROR", status=400, safe=False)