from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import DeleteView, DetailView, CreateView
from django.urls import reverse_lazy

from ...models import *
from ..autorization import *


def organizations(request):
    return None


def organizations_detail(request):
    return None


def organizations_registration(request):
    return None
