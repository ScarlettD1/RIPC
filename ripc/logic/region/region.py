from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render

from .regionForm import RegisterRegionForm
from ...models import *


# Функция отображения списка регионов с проверкой на авторизацию
@login_required(login_url='/accounts/login/')
def regions(request):
    region_list = Region.objects.all()
    form = RegisterRegionForm()
    return render(request, 'structure/regions/region_list.html', {'regions': region_list, 'form': form})


# Функция отображения детальной страницы региона
@login_required(login_url='/accounts/login/')
def regions_detail(request, reg_id):
    org_list = Organization.objects.filter(region=reg_id)
    reps_list = RegionRep.objects.filter(region=reg_id)
    region = get_object_or_404(Region, pk=reg_id)
    return render(request, 'structure/regions/region_detail.html',
                  {'orgs': org_list, 'region': region, 'reps': reps_list})


# Функция отображения формы добавления региона
@login_required(login_url='/accounts/login/')
def regions_reg(request):
    if request.method == "POST":
        form = RegisterRegionForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            Region.create(name=name)
            return HttpResponseRedirect('/regions/')
        else:
            return JsonResponse({'errors': form.errors}, status=400)


# Функция отображения страницы редактирования региона
@login_required(login_url='/accounts/login/')
def regions_edit(request, reg_id):
    reg = get_object_or_404(Region, pk=reg_id)
    return render(request, 'structure/regions/region_edit.html', {'reg': reg})
