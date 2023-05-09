from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from ripc.models import OrganizationEvent, Event, EventStatus, Organization
from ripc.serializers import OrganizationEventSerializer, EventSerializer


def __complete_data(event_organizations_data):
    for i, event_organization in enumerate(event_organizations_data):
        event_organizations_data[i]['event_status'] = EventStatus.objects.filter(id=event_organization['event_status'])[0].__dict__
        event_organizations_data[i]['event_status'].pop('_state')
        event_organizations_data[i]['organization'] = Organization.objects.filter(id=event_organization['organization'])[0].__dict__
        event_organizations_data[i]['organization'].pop('_state')
    return event_organizations_data


@login_required(login_url='/accounts/login/')
def view_event_organization(request, event_id):
    context = {}

    event = Event.objects.get(id=event_id)
    event_serializer = EventSerializer(event, many=False)
    event_data = event_serializer.data
    event_data['start_date'] = str(datetime.strptime(event_data['start_date'], '%Y-%m-%d').date().strftime("%d.%m.%Y"))
    event_data['end_date'] = str(datetime.strptime(event_data['end_date'], '%Y-%m-%d').date().strftime("%d.%m.%Y"))
    context['event'] = event_data

    event_organizations = OrganizationEvent.objects.filter(event=event_id)
    event_organizations_serializer = OrganizationEventSerializer(event_organizations, many=True)
    context['event_organizations'] = __complete_data(event_organizations_serializer.data)

    return render(request, 'main_pages/event_organization.html', context)


@csrf_exempt
def event_organizations_api(request):
    if request.method == "GET":
        query = {}
        # Поиск query
        ids = request.GET.get('id')
        if ids and len(ids.split(',')) > 1:
            ids = ids.split(',')

        events = request.GET.get('event')
        if events and len(events.split(',')) > 1:
            events = events.split(',')

        organizations = request.GET.get('organizations')
        if organizations and len(organizations.split(',')) > 1:
            organizations = organizations.split(',')

        if ids:
            query['id__in'] = ids if type(ids) is list else [ids]

        if events:
            query['event__in'] = events if type(events) is list else [events]

        if organizations:
            query['organizations__in'] = organizations if type(organizations) is list else [organizations]

        # Если query заполнен
        if query:
            event_organizations = OrganizationEvent.objects.filter(**query)
            event_organizations_serializer = OrganizationEventSerializer(event_organizations, many=True)
            event_organizations_data = __complete_data(event_organizations_serializer.data)
            return JsonResponse(event_organizations_data, status=200, safe=False)

        # Если query нет
        event_organizations = OrganizationEvent.objects.all()
        event_organizations_serializer = OrganizationEventSerializer(event_organizations, many=True)
        event_organizations_data = __complete_data(event_organizations_serializer.data)
        return JsonResponse(event_organizations_data, status=200, safe=False)

    elif request.method == "POST":
        # Поиск query
        get_full = request.GET.get('get_full')

        datas = []
        event_organization_result = []
        event_organizations_data = JSONParser().parse(request)
        if type(event_organizations_data) is dict:
            datas.append(event_organizations_data)
        else:
            datas = event_organizations_data

        for data in datas:
            event_organizations_serializer = OrganizationEventSerializer(data=data)
            if not event_organizations_serializer.is_valid():
                return JsonResponse("ERROR", status=500, safe=False)
            event_organizations_serializer.save()

            if get_full:
                event_organization_result.append(__complete_data([event_organizations_serializer.data]))
            else:
                event_organization_result.append(event_organizations_serializer.data.get('id'))

        return JsonResponse(event_organization_result, status=200, safe=False)

    elif request.method == "PUT":
        datas = []
        event_organizations_data = JSONParser().parse(request)
        if type(event_organizations_data) is dict:
            datas.append(event_organizations_data)
        else:
            datas = event_organizations_data

        for data in datas:
            event_organizations = OrganizationEvent.objects.get(id=data['id'])
            event_organizations_serializer = OrganizationEventSerializer(event_organizations, data=data)
            if event_organizations_serializer.is_valid():
                event_organizations_serializer.save()
        return JsonResponse("OK", status=200, safe=False)

    elif request.method == "DELETE":
        ids = request.GET.get('id')
        if ids and len(ids.split(',')) > 1:
            ids = ids.split(',')
        else:
            ids = [ids]

        for id in ids:
            event_organizations = OrganizationEvent.objects.get(id=id)
            event_organizations.delete()
        return JsonResponse("OK", status=200, safe=False)
