from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:id>/', views.detail, name='detail'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('test', views.test, name='test'),
]