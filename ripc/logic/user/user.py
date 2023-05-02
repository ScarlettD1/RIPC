from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from ...models import *


@login_required(login_url='/accounts/login/')
def users(request):
    region_list = Region.objects.all()
    return render(request, 'structure/regions/region_list.html', {'regions': region_list})


@login_required(login_url='/accounts/login/')
def users_detail(request, reg):
    org_list = Organization.objects.filter(region=reg)
    region = get_object_or_404(Region, pk=reg)
    return render(request, 'structure/regions/region_detail.html', {'orgs': org_list, 'region': region})


@login_required(login_url='/accounts/login/')
def users_reg(request):
    if request.method == "POST":
        Region.create(name=request.POST.get("region_name"))
    return HttpResponseRedirect('/personnel/regions/')


@login_required(login_url='/accounts/login/')
def users_edit(request):
    return None
