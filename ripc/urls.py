from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('create_event/', views.create_event, name='create_event'),
    path('personnel/users/', views.users, name='users'),
    path('personnel/users/<int:id>', views.user_detail, name='user_page'),
    path('personnel/users/registration/', views.user_reg, name='user_reg'),
    path('personnel/regions/', views.regions, name='regions'),
    path('personnel/regions/registration/', views.regions_registration, name='regions_reg'),
    path('personnel/regions/<int:id>', views.regions_detail, name='regions_detail'),
    path('personnel/organizations/', views.organizations, name='orgs'),
    path('personnel/organizations/registration/', views.organizations_registration, name='org_reg'),
    path('personnel/organizations/<int:id>', views.organizations_detail, name='orgs_detail'),
]
