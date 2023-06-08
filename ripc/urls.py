from django.urls import path, include

from . import views
from .logic.region import region
from .logic.organization import organization
from .logic.expert import expert

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('create_event/', views.create_event, name='create_event'),
    path('experts/', expert.experts, name='experts'),
    path('experts/<int:expert_id>', expert.experts_detail, name='experts_detail'),
    path('experts/reg/', expert.experts_reg, name='experts_reg'),
    path('regions/', region.regions, name='regions'),
    path('regions/edit/<int:reg_id>', region.regions_edit, name='regions_edit'),
    path('regions/<int:reg_id>', region.regions_detail, name='regions_detail'),
    path('regions/reg', region.regions_reg, name='regions_reg'),
    path('organizations/', organization.organizations, name='orgs'),
    path('organizations/reg/', organization.organizations_registration, name='org_reg'),
    path('organizations/edit/<int:org_id>', organization.organizations_edit, name='orgs_edit'),
    path('organizations/<int:org_id>', organization.organizations_detail, name='orgs_detail'),
]
