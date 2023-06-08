from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from .expertForm import RegisterExpertForm
from ..userForm import RegisterUserForm
from ...models import *


@login_required(login_url='/accounts/login/')
def experts(request):
    expert_list = Expert.objects.all()
    return render(request, 'structure/experts/expert_list.html', {'experts': expert_list})


@login_required(login_url='/accounts/login/')
def experts_detail(request, expert_id):
    expert = get_object_or_404(Expert, pk=expert_id)
    return render(request, 'structure/regions/region_detail.html', {'expert': expert})


@login_required(login_url='/accounts/login/')
def experts_reg(request):
    if request.method == "POST":
        expert_form = RegisterExpertForm(request.POST)
        user_form = RegisterUserForm(request.POST)
        if expert_form.is_valid() and user_form.is_valid():
            Expert.create(request.POST)
            return HttpResponseRedirect('/experts/')
    else:
        expert_form = RegisterExpertForm()
        user_form = RegisterUserForm()
    return render(request, "structure/experts/expert_reg.html", {'expert_form': expert_form, 'user_form': user_form})


@login_required(login_url='/accounts/login/')
def experts_edit(request):
    return None
