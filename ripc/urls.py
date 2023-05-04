from django.urls import path, re_path, include

from . import views
from .logic.pattern_task import pattern_task
from .logic.region import region
from .logic.organization import organization
from .logic.event import event
from .logic.subject import subject
from .logic.variant import variant

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('personnel/users/', views.users, name='users'),
    path('personnel/users/<int:id>', views.user_detail, name='user_page'),
    path('personnel/users/registration/', views.user_reg, name='user_reg'),
    path('personnel/regions/', region.regions, name='regions'),
    path('personnel/regions/edit/', region.regions_edit, name='regions_edit'),
    path('personnel/regions/<int:id>', region.regions_detail, name='regions_detail'),
    path('personnel/regions/reg', region.regions_reg, name='regions_reg'),
    path('personnel/organizations/', organization.organizations, name='orgs'),
    path('personnel/organizations/reg/', organization.organizations_registration, name='org_reg'),
    path('personnel/organizations/<int:id>', organization.organizations_detail, name='orgs_detail'),
    re_path(r'api/subject/(<int:id>)?', subject.subject_api, name='subject_api'),
    re_path(r'api/event/(<int:id>)?', event.event_api_get, name='event_api_get'),
    path('api/event', event.event_api_post, name='event_api_post'),
    path('api/variant/<id>', variant.variant_api_get, name='variant_api_get'),
    path('api/variant', variant.variant_api_post, name='variant_api_post'),
    re_path(r'api/pattern_task/(<int:id>)?', pattern_task.pattern_api_get, name='pattern_api_get'),
    path('api/pattern_task', pattern_task.pattern_api_post, name='pattern_api_post'),


    # Страницы
    path('create_event', event.create_event, name='create_event'),
    path('event/<int:event_id>', event.view_event, name='view_event'),
]
