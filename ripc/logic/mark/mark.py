from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from ...models import *


@login_required(login_url='/accounts/login/')
def marking(request, event_id):
    expert_list = Expert.objects.all()
    return render(request, 'main_pages/marking.html', {'experts': expert_list})
