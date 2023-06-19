from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DeleteView, DetailView, CreateView
from django.urls import reverse_lazy

from .orgForm import RegisterOrgForm
from ..required import some_resp_required
from ...models import *
from ..autorization import *
from ...serializers import OrganizationSerializer


@login_required(login_url='/accounts/login/')
def organizations(request):
    org_list = Organization.objects.all()
    form = RegisterOrgForm()
    return render(request, 'structure/organizations/org_list.html', {'orgs': org_list, 'form': form})


@login_required(login_url='/accounts/login/')
def organizations_detail(request, org_id):
    org = get_object_or_404(Organization, pk=org_id)
    return render(request, 'structure/organizations/org_detail.html', {'org': org})


@login_required(login_url='/accounts/login/')
def organizations_registration(request):
    if request.method == "POST":
        form = RegisterOrgForm(request.POST)
        if form.is_valid():
            region = Region.objects.get(pk=request.POST.get("region"))
            Organization.create(name=request.POST.get("name"), region=region)
            return HttpResponseRedirect('/organizations/')


@login_required(login_url='/accounts/login/')
def organizations_edit(request):
    return None


@csrf_exempt
@login_required(login_url='/accounts/login/')
@some_resp_required(login_url='/accounts/login/')
def organizations_api(request):
    if request.method == "GET":
        query = {}
        # Поиск query
        ids = request.GET.get('id')
        if ids and len(ids.split(',')) > 1:
            ids = ids.split(',')

        if request.user.is_superuser:
            query['region'] = 1
        else:
            query['region'] = RegionRep.objects.filter(user=request.user.id)[0].region_id

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