from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from ripc.logic.check_who_auth import region_rep_authenticated, org_rep_authenticated
from ripc.logic.required import some_resp_required, region_resp_required
from ripc.models import Subject, Event, OrganizationEvent, ScannedPage, Complect, Variant, OrganizationRep, RegionRep, \
    Organization, Region, PatternTask, Criteria
from ripc.serializers import EventSerializer, OrganizationEventSerializer, ScannedPageSerializer, ComplectSerializer, \
    PatternTaskSerializer, VariantSerializer, CriteriaSerializer, SubjectSerializer


@login_required(login_url='/accounts/login/')
@region_resp_required(login_url='/accounts/login/')
def create_event(request):
    context = {}
    return render(request, 'main_pages/create_event.html', context)


@login_required(login_url='/accounts/login/')
@region_resp_required(login_url='/accounts/login/')
def edit_event(request, event_id):
    context = {}

    event = Event.objects.filter(id=event_id).first()
    if not event:
        return JsonResponse("Event not found!", status=404, safe=False)

    event_serializer = EventSerializer(event, many=False)
    event_data = event_serializer.data
    event_data['start_date'] = str(datetime.strptime(event_data['start_date'], '%Y-%m-%d').date().strftime("%d.%m.%Y"))
    event_data['end_date'] = str(datetime.strptime(event_data['end_date'], '%Y-%m-%d').date().strftime("%d.%m.%Y"))
    context['event'] = event_data

    variants = Variant.objects.filter(event=event_id)
    variants_data = VariantSerializer(variants, many=True).data
    context['variants'] = variants_data

    for i, variant in enumerate(variants_data):
        context['variants'][i]['file_name'] = variant['file_path'].split('&&')[1]
        criteria = Criteria.objects.get(variant=variant['id'])
        criteria_data = CriteriaSerializer(criteria, many=False).data
        criteria_data['file_name'] = criteria_data['file_path'].split('&&')[1]
        context['variants'][i]['criteria_obj'] = criteria_data

    subjects = Subject.objects.all()
    subjects_data = SubjectSerializer(subjects, many=True).data
    context['subjects'] = subjects_data

    pattern_tasks = PatternTask.objects.filter(event=event_id)
    pattern_tasks_data = PatternTaskSerializer(pattern_tasks, many=True).data
    context['pattern_tasks'] = pattern_tasks_data

    return render(request, 'main_pages/edit_event.html', context)


@login_required(login_url='/accounts/login/')
@some_resp_required(login_url='/accounts/login/')
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
    scanned_pages = ScannedPage.objects.filter(organization_event=event_organizations_serializer.data['id']).order_by(
        'page_number')
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
        context['complect'][complect_id]['pages'][int(page['page_number']) - 1] = page

    return render(request, 'main_pages/view_event.html', context)


@login_required(login_url='/accounts/login/')
@some_resp_required(login_url='/accounts/login/')
def view_events(request):
    context = {}

    who_auth = None

    if request.user.is_superuser:
        who_auth = "admin"
        if request.GET.get('organization_id'):
            who_auth = "org_rep"

    elif region_rep_authenticated(request.user):
        who_auth = "region_rep"
    elif org_rep_authenticated(request.user):
        who_auth = "org_rep"
    else:
        return JsonResponse("ERROR AUTH!", status=403, safe=False)

    if who_auth in ["admin", "region_rep"]:
        region_id = 0
        if who_auth == "admin":
            region_id = 1

        elif who_auth == "region_rep":
            # Получаем по ID региона
            region_id = RegionRep.objects.filter(user=request.user.id)[0].region_id

        # Поиск имени региона
        if region_id:
            region = Region.objects.filter(id=region_id)[0]
            context['region_name'] = region.name
            return render(request, 'main_pages/events_resp.html', context)

        else:
            return JsonResponse("Region not found!", status=404, safe=False)

    if who_auth == "org_rep":
        if request.GET.get('organization_id'):
            organization_id = request.GET.get('organization_id')
        else:
            # Получаем ID организации
            organization = OrganizationRep.objects.filter(user=request.user.id)
            if not organization:
                return JsonResponse("OrganizationRep not found!", status=404, safe=False)
            organization_id = organization[0].organization_id

        # Поиск имени организации
        if organization_id:
            organization = Organization.objects.filter(id=organization_id)[0]
            context['organization_name'] = organization.name
            return render(request, 'main_pages/events_org.html', context)
        else:
            return JsonResponse("Organization not found!", status=404, safe=False)



@csrf_exempt
@login_required(login_url='/accounts/login/')
@some_resp_required(login_url='/accounts/login/')
def event_api(request, id=0):
    if request.method == "GET":
        # Поиск query
        ids = request.GET.get('id')

        if ids:
            events = Event.objects.get(id=ids)
            events_serializer_data = EventSerializer(events, many=False).data
            events_serializer_data['start_date'] = str(datetime.strptime(events_serializer_data['start_date'], '%Y-%m-%d').date().strftime("%d.%m.%Y"))
            events_serializer_data['end_date'] = str(datetime.strptime(events_serializer_data['end_date'], '%Y-%m-%d').date().strftime("%d.%m.%Y"))
            return JsonResponse(events_serializer_data, status=200, safe=False)

        else:
            context = {}
            context['events'] = []
            context['total_page'] = 1

            page_number = request.GET.get("page")

            # Поиск ID региона
            region_id = 0
            if request.user.is_superuser:
                region_id = 1
            elif region_rep_authenticated(request.user):
                # Получаем по ID региона
                region_id = RegionRep.objects.filter(user=request.user.id)[0].region_id

            # Поиск МП по region_id
            events_serializer_data = None
            if region_id:
                events = Event.objects.filter(region=region_id).order_by("start_date")
                if page_number:
                    events_paginator = Paginator(events, 15)
                    context['total_page'] = events_paginator.num_pages
                    page_obj = events_paginator.get_page(page_number)
                    events_serializer_data = EventSerializer(page_obj, many=True).data
                else:
                    events_serializer_data = EventSerializer(events, many=True).data

            if not events_serializer_data:
                return JsonResponse(context, status=200, safe=False)

            # Расчёт информации для МП
            for event in events_serializer_data:
                orgs_event = OrganizationEvent.objects.filter(event=event['id'])
                orgs_event_data = OrganizationEventSerializer(orgs_event, many=True).data

                orgs_count = len(orgs_event_data)
                total_percent = 0
                for org in orgs_event_data:
                    # Расчёт общего процента
                    total_percent += int(org['percent_status'])
                if orgs_count:
                    total_percent = int(total_percent / orgs_count)

                # Проверка заполненности всех данных
                not_create = False
                variants = Variant.objects.filter(event=event['id'])
                patterns = PatternTask.objects.filter(event=event['id'])
                criteria = []
                for variant in variants:
                    criteria.append(Criteria.objects.filter(variant=variant.id))

                if not variants or not patterns or len(criteria) != len(variants):
                    not_create = True

                context['events'].append({
                    'id': event['id'],
                    'name': event['name'],
                    'start_date': str(datetime.strptime(event['start_date'], '%Y-%m-%d').date().strftime("%d.%m.%Y")),
                    'end_date': str(datetime.strptime(event['end_date'], '%Y-%m-%d').date().strftime("%d.%m.%Y")),
                    'orgs_count': orgs_count,
                    'total_percent': total_percent,
                    'not_create': not_create
                })
            return JsonResponse(context, status=200, safe=False)

        return JsonResponse("ERROR", status=400, safe=False)

    if request.method == "POST" and region_rep_authenticated(request.user):
        event_data = JSONParser().parse(request)
        event_data['start_date'] = str(datetime.strptime(event_data['start_date'], '%d.%m.%Y').date())
        event_data['end_date'] = str(datetime.strptime(event_data['end_date'], '%d.%m.%Y').date())
        if request.user.is_superuser:
            event_data['region'] = 1
        else:
            event_data['region'] = RegionRep.objects.filter(user=request.user.id)[0].region_id

        events_serializer = EventSerializer(data=event_data)
        if not events_serializer.is_valid():
            return JsonResponse("ERROR", status=500, safe=False)

        events_serializer.save()
        return JsonResponse(events_serializer.data.get("id"), status=200, safe=False)

    if request.method == "PUT" and region_rep_authenticated(request.user):
        event_data = JSONParser().parse(request)
        event_old = Event.objects.get(id=id)

        event_data['start_date'] = str(datetime.strptime(event_data['start_date'], '%d.%m.%Y').date())
        event_data['end_date'] = str(datetime.strptime(event_data['end_date'], '%d.%m.%Y').date())
        event_data['region'] = event_old.region_id

        events_serializer = EventSerializer(event_old, data=event_data)
        if not events_serializer.is_valid():
            print(events_serializer.errors)
            return JsonResponse("ERROR", status=500, safe=False)

        events_serializer.save()
        return JsonResponse(events_serializer.data.get("id"), status=200, safe=False)

    if request.method == "DELETE" and region_rep_authenticated(request.user):
        ids = request.GET.get('id')
        if ids and len(ids.split(',')) > 1:
            ids = ids.split(',')
        else:
            ids = [ids]

        for id in ids:
            event = Event.objects.get(id=id)
            event.delete()
        return JsonResponse("OK", status=200, safe=False)

    return JsonResponse("Method not allowed", status=400, safe=False)
