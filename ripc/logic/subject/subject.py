from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from ripc.models import Subject
from ripc.serializers import SubjectSerializer


@csrf_exempt
def subject_api(request, id=0):
    if request.method == "GET":
        subjects = Subject.objects.all()
        subjects_serializer = SubjectSerializer(subjects, many=True)
        return JsonResponse(subjects_serializer.data, status=200, safe=False)
    elif request.method == "POST":
        subject_data = JSONParser().parse(request)
        print(subject_data)
        subjects_serializer = SubjectSerializer(data=subject_data)
        if subjects_serializer.is_valid():
            subjects_serializer.save()
            return JsonResponse("OK", status=200, safe=False)
    #     return JsonResponse("ERROR", status=400, safe=False)
    # elif request.method == "PUT":
    #     subject_data = JSONParser().parse(request)
    #     subject = Subject.objects.get(id=subject_data['id'])
    #     subjects_serializer = SubjectSerializer(subject, data=subject_data)
    #     if subjects_serializer.is_valid():
    #         subjects_serializer.save()
    #         return JsonResponse("OK", status=200, safe=False)
    #     return JsonResponse("ERROR", status=400, safe=False)
    # elif request.method == "DELETE":
    #     subject = Subject.objects.get(id=id)
    #     subject.delete()
    #     return JsonResponse("ERROR", status=400, safe=False)