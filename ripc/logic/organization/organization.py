from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render, redirect

from ...models import *


@login_required(login_url='/accounts/login/')
def organizations(request):
    org_list = Organization.objects.all()
    return render(request, 'structure/organizations/org_list.html', {'orgs': org_list})


@login_required(login_url='/accounts/login/')
def organizations_detail(request):
    return None


@login_required(login_url='/accounts/login/')
def organizations_registration(request):
    return None


@login_required(login_url='/accounts/login/')
def organizations_edit(request):
    return None
