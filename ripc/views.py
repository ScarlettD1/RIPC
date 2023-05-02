from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import DeleteView, DetailView, CreateView
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from rest_framework.parsers import JSONParser

from .models import Expert, Subject
from .logic.autorization import *
from .models import *
from .forms import RegisterUserForm
from .serializers import SubjectSerializer


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


# Роуты базы данных
@csrf_exempt
@login_required(login_url='/accounts/login/')
def subject_api(request, id=0):
    if request.method == "GET":
        subjects = Subject.objects.all()
        subjects_serializer = SubjectSerializer(subjects, many=True)
        return JsonResponse(subjects_serializer.data, status=200, safe=False)
    # elif request.method == "POST":
    #     subject_data = JSONParser().parse(request)
    #     subjects_serializer = SubjectSerializer(data=subject_data)
    #     if subjects_serializer.is_valid():
    #         subjects_serializer.save()
    #         return JsonResponse("OK", status=200, safe=False)
    #     return JsonResponse("ERROR", status=400, safe=False)
    # elif request.method == "PUT":
    #     subject_data = JSONParser().parse(request)
    #     subject = Subject.objects.get(id=subject_data['id'])
    #     subjects_serializer = SubjectSerializer(subject, data=subject_data)
    #     if subjects_serializer.is_valid():
    #         subjects_serializer.save()
    #         return JsonResponse("OK", status=200, safe=False)
    #     return JsonResponse("ERROR", status=400, safe=False)
    # elif request.method == "DELETE":
    #     subject = Subject.objects.get(id=id)
    #     subject.delete()
    #     return JsonResponse("ERROR", status=400, safe=False)

