from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DeleteView, DetailView, CreateView
from django.urls import reverse_lazy

from ...models import *
from ..autorization import *
from ...serializers import OrganizationSerializer


def organizations(request):
    return None


def organizations_detail(request):
    return None


def organizations_registration(request):
    return None


@csrf_exempt
def organizations_api(request):
    if request.method == "GET":
        query = {}
        # Поиск query
        ids = request.GET.get('id')
        if ids and len(ids.split(',')) > 1:
            ids = ids.split(',')

        if ids:
            query['id__in'] = ids

        if query:
            organizations = Organization.objects.filter(**query)
            organizations_serializer = OrganizationSerializer(organizations, many=True)
            return JsonResponse(organizations_serializer.data, status=200, safe=False)


        # Если query нет
        organizations = Organization.objects.all()
        organizations_serializer = OrganizationSerializer(organizations, many=True)
        return JsonResponse(organizations_serializer.data, status=200, safe=False)