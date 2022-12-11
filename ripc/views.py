from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render

from .models import Expert


def is_not_expert(user):
    pass
    # return user.role !== expert


@login_required(login_url='/accounts/login/')
def index(request):
    return render(request, 'ripc/index.html', )


@user_passes_test(is_not_expert)  # проверка на права, для захода на страницу
@login_required(login_url='/accounts/login/')
def detail(request, question_id):
    expert_name = get_object_or_404(Expert, pk=question_id)
    return render(request, 'ripc/detail.html', {'name': expert_name})
