from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url='/accounts/login/')
def create_event(request):
    context = {}
    return render(request, 'main_pages/create_event.html', context)


@login_required(login_url='/accounts/login/')
def view_event(request, event_id):
    context = {}
    return render(request, 'main_pages/view_event.html', context)