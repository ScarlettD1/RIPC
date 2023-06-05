from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import DeleteView, DetailView, CreateView
from django.urls import reverse_lazy

from ...models import *
from ..autorization import *

def rate(request):
    return render(request, 'estimating_pages/estimate.html')