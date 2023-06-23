from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from ...models import *


# Функция отображения страницы проверки с отборкой 10 ответов с сортировкой по заданию и варианту
@login_required(login_url='/accounts/login/')
def marking(request, event_id):
    context = {}
    answer_list = Answer.objects.order_by("task__number").all().order_by('task__variant').filter(mark=None)[:10]
    context['answers'] = answer_list
    return render(request, 'main_pages/marking.html', context)
