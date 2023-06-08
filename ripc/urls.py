from django.urls import path, include
from django.contrib.auth import views as authViews

from . import views
from .logic.complect import complect
from .logic.criteria import criteria
from .logic.event_organization import event_organization
from .logic.pattern_task import pattern_task
from .logic.region import region
from .logic.organization import organization
from .logic.event import event
from .logic.scanned_page import scanned_page
from .logic.scanner import scanner
from .logic.subject import subject
from .logic.task import task
from .logic.variant import variant
from .logic.variant_cropping import variant_cropping

urlpatterns = [
    path('logout/', authViews.LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
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
    path('api/event/<int:id>', event.event_api, name='event_api'),
    path('api/variant/', variant.variant_api, name='variant_api_post'),
    path('api/variant/file/<int:id>', variant.variant_api_file, name='variant_api_file'),
    path('api/cropping_variant/start/<int:id>', variant_cropping.start_cropping_variant, name='start_cropping_variant'),
    path('api/cropping_variant/image/<int:id>', variant_cropping.cropping_variant_image, name='cropping_variant_image'),
    path('api/pattern_task/', pattern_task.pattern_api, name='pattern_api'),
    path('api/task/', task.task_api, name='task_api'),
    path('api/organization/', organization.organizations_api, name='organizations_api'),
    path('api/event_organization/', event_organization.event_organizations_api, name='event_organizations_api'),
    path('api/complect_scan/', scanned_page.complect_scan_data, name='complect_scan_data'),
    path('api/scanned_page/file/<int:id>', scanned_page.scanned_api_file, name='scanned_api_file'),
    path('api/scanned_page/files/<int:id>', scanned_page.scanned_api_files, name='scanned_api_files'),
    path('api/scanned_page/<int:id>', scanned_page.scanned_api, name='scanned_api'),
    path('api/scanned_page/scan', scanned_page.file_from_scanner, name='file_from_scanner'),
    path('api/complects/generate', complect.complects_generate, name='complects_generate'),
    path('api/criteria/', criteria.criteria_api, name='criteria_api'),
    path('api/criteria/file/<int:id>', criteria.criteria_api_file, name='criteria_api_file'),

    # Страницы
    path('', views.index, name='index'),
    path('create_event', event.create_event, name='create_event'),
    path('edit_event/<int:event_id>/', event.edit_event, name='edit_event'),
    path('event/<int:event_id>/', event.view_event, name='view_event'),
    path('event_organization/<int:event_id>', event_organization.view_event_organization, name='view_event_organization'),
    path('events', event.view_events, name='view_events'),

    # Скачивание Scanner
    path('scanner/download/', scanner.scanner_download, name='scanner_download'),

    # Скачивание комплектов
    path('complects/download/<int:event_id>', complect.complects_download, name='complects_download'),

]
