from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import DeleteView, DetailView, CreateView
from django.urls import reverse_lazy

from ...models import *
from ..autorization import *


def regions(request):
    region_list = Region.objects.all()
    return render(request, 'structure/regions/region_list.html', {'regions': region_list})


def regions_detail(request):
    return None


def regions_reg(request):
    if request.method == "POST":
        r = Region(name=request.POST.get("region_name"))
        r.save()
    return {'status': 'success'}


def regions_edit(request):
    return None
