from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from ripc.logic.check_who_auth import region_rep_authenticated
from ripc.logic.required import some_rep_required, region_rep_required
from ripc.models import Subject, Event, OrganizationEvent, ScannedPage, Complect, Variant, OrganizationRep
from ripc.serializers import EventSerializer, OrganizationEventSerializer, ScannedPageSerializer, ComplectSerializer


@login_required(login_url='/accounts/login/')
@region_rep_required(login_url='/accounts/login/')
def create_event(request):
    context = {}
    return render(request, 'main_pages/create_event.html', context)


@login_required(login_url='/accounts/login/')
@some_rep_required(login_url='/accounts/login/')
def view_event(request, event_id):
    context = {}

    # Поиск id организации
    organization_id = request.GET.get('organization_id')
    if not organization_id:
        user_org = OrganizationRep.objects.filter(user=request.user.id).first()
        organization_id = user_org.organization_id

    # Получаем имформацию о МП
    event = Event.objects.get(id=event_id)
    event_serializer = EventSerializer(event, many=False)
    event_data = event_serializer.data
    event_data['start_date'] = str(datetime.strptime(event_data['start_date'], '%Y-%m-%d').date().strftime("%d.%m.%Y"))
    event_data['end_date'] = str(datetime.strptime(event_data['end_date'], '%Y-%m-%d').date().strftime("%d.%m.%Y"))
    context['event'] = event_data

    # Получаем имформацию об организации в МП
    event_organizations = OrganizationEvent.objects.filter(event=event_id, organization=organization_id)[0]
    event_organizations_serializer = OrganizationEventSerializer(event_organizations, many=False)
    context['event_organizations'] = event_organizations_serializer.data

    # Получаем имформацию о комплетках МП
    complects = Complect.objects.filter(organization_event=event_organizations_serializer.data['id'])
    complects_serializer = ComplectSerializer(complects, many=True)
    complects_data = complects_serializer.data

    # Генерируем списки для комплектов
    context['complect'] = {}
    for complect in complects_data:
        complect_id = str(complect['id'])
        variant_id = str(complect['variant'])
        variant_data = Variant.objects.filter(id=variant_id).first()
        context['complect'][complect_id] = {
            'pages': [[] for i in range(int(variant_data.page_count))],
            'is_additional': complect['is_additional']
        }

    # Получаем имформацию об отсканированных страницах МП
    scanned_pages = ScannedPage.objects.filter(organization_event=event_organizations_serializer.data['id']).order_by('page_number')
    scanned_pages_serializer = ScannedPageSerializer(scanned_pages, many=True)
    scanned_pages_data = scanned_pages_serializer.data

    context['error_scanned_page'] = []
    for page in scanned_pages_data:
        # Поиск нераспознанных страницах
        if not page['complect']:
            context['error_scanned_page'].append(page)
            continue

        # Заполнение распознанных страниц
        complect_id = str(page['complect'])
        context['complect'][complect_id]['pages'][int(page['page_number'])-1] = page

    return render(request, 'main_pages/view_event.html', context)


@csrf_exempt
@login_required(login_url='/accounts/login/')
@some_rep_required(login_url='/accounts/login/')
def event_api(request):
    if request.method == "GET":
        # Поиск query
        ids = request.GET.get('id')

        if ids:
            events = Event.objects.get(id=ids)
            events_serializer = EventSerializer(events, many=False)
        else:
            events = Subject.objects.all()
            events_serializer = EventSerializer(events, many=True)

        return JsonResponse(events_serializer.data, status=200, safe=False)

    if request.method == "POST" and region_rep_authenticated(request.user):
        event_data = JSONParser().parse(request)
        if event_data.get('start_date'):
            event_data['start_date'] = str(datetime.strptime(event_data['start_date'], '%d.%m.%Y').date())
        if event_data.get('end_date'):
            event_data['end_date'] = str(datetime.strptime(event_data['end_date'], '%d.%m.%Y').date())

        events_serializer = EventSerializer(data=event_data)
        if not events_serializer.is_valid():
            return JsonResponse("ERROR", status=500, safe=False)

        events_serializer.save()
        return JsonResponse(events_serializer.data.get("id"), status=200, safe=False)
    return JsonResponse("Method not allowed", status=400, safe=False)