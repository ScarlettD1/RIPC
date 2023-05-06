from django.urls import path, re_path, include

from . import views
from .logic.pattern_task import pattern_task
from .logic.region import region
from .logic.organization import organization
from .logic.event import event
from .logic.subject import subject
from .logic.task import task
from .logic.variant import variant
from .logic.variant_cropping import variant_cropping

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
    path('api/subject/', subject.subject_api, name='subject_api'),
    path('api/event/', event.event_api, name='event_api'),
    path('api/variant/', variant.variant_api, name='variant_api_post'),
    path('api/variant/file/<int:id>', variant.variant_api_file, name='variant_api_file'),
    path('api/cropping_variant/start/<int:id>', variant_cropping.start_cropping_variant, name='start_cropping_variant'),
    path('api/cropping_variant/image/<int:id>', variant_cropping.cropping_variant_image, name='cropping_variant_image'),
    path('api/pattern_task/', pattern_task.pattern_api, name='pattern_api'),
    path('api/task/', task.task_api, name='task_api'),

    # Страницы
    path('create_event', event.create_event, name='create_event'),
    path('event/<int:event_id>', event.view_event, name='view_event'),
]
