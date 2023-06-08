from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect

from .orgForm import RegisterOrgForm
from ...models import *


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
