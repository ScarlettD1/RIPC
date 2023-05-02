from django.urls import path, include

from . import views
from .logic.region import region
from .logic.organization import organization

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('create_event/', views.create_event, name='create_event'),
    path('personnel/users/', views.users, name='users'),
    path('personnel/users/<int:id>', views.user_detail, name='user_page'),
    path('personnel/users/registration/', views.user_reg, name='user_reg'),
    path('personnel/regions/', region.regions, name='regions'),
    path('personnel/regions/edit/<int:id>', region.regions_edit, name='regions_edit'),
    path('personnel/regions/<int:reg>', region.regions_detail, name='regions_detail'),
    path('personnel/regions/reg', region.regions_reg, name='regions_reg'),
    path('personnel/organizations/', organization.organizations, name='orgs'),
    path('personnel/organizations/reg/', organization.organizations_registration, name='org_reg'),
    path('personnel/organizations/edit/<int:id>', organization.organizations_edit, name='orgs_edit'),
    path('personnel/organizations/<int:id>', organization.organizations_detail, name='orgs_detail'),
]
