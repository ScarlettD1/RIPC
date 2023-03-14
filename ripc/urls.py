from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:id>/', views.detail, name='detail'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('create_event', views.create_event, name='create_event'),
    path('event/<int:event_id>', views.view_event, name='view_event'),
]
