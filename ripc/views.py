from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import DeleteView, DetailView, CreateView
from django.urls import reverse_lazy
from .logic.autorization import *
from .models import *
from .forms import RegisterUserForm


def is_not_expert(user):
    return True
    # return user.role !== expert


def is_admin(user):
    return True
    # return user.role !== expert


@login_required(login_url='/accounts/login/')
def index(request):
    context = {'user': request.user}
    return render(request, 'ripc/index.html', context)


@user_passes_test(is_not_expert)  # проверка на права, для захода на страницу
@login_required(login_url='/accounts/login/')
def detail(request, question_id):
    expert_name = get_object_or_404(Expert, pk=question_id)
    return render(request, 'ripc/detail.html', {'name': expert_name})


@user_passes_test(is_admin)
@login_required(login_url='/accounts/login/')
def create_event(request):
    context = {}
    return render(request, 'main_pages/create_event.html', context)


@user_passes_test(is_not_expert)
@login_required(login_url='/accounts/login/')
def view_event(request, event_id):
    context = {}
    return render(request, 'main_pages/view_event.html', context)


@user_passes_test(is_admin)
@login_required(login_url='/accounts/login')
def admin_event(request):
    contex = {}
    return render(request, 'main_pages/admin_event.html', contex)


@user_passes_test(is_admin)
@login_required(login_url='/accounts/login/')
class RegisterUserView(CreateView):
    form_class = RegisterUserForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form_valid = super().form_valid(form)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        auth_user = authenticate(username=username, password=password)
        login(self.request, auth_user)
        return form_valid

    def get_success_url(self):
        return self.success_url


def users(request):
    return None


def user_detail(request):
    return None


def user_reg(request):
    return None


def user_detail(request):
    return None
