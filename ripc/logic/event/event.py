from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from ripc.models import Subject, Event, OrganizationEvent
from ripc.serializers import EventSerializer, OrganizationEventSerializer


@login_required(login_url='/accounts/login/')
def create_event(request):
    context = {}
    return render(request, 'main_pages/create_event.html', context)


@login_required(login_url='/accounts/login/')
def view_event(request, event_id):
    context = {}

    # Поиск query
    organization_id = request.GET.get('organization_id')

    event_organizations = OrganizationEvent.objects.filter(event=event_id, organization=organization_id)[0]
    event_organizations_serializer = OrganizationEventSerializer(event_organizations, many=False)
    context['event_organizations'] = event_organizations_serializer.data

    event = Event.objects.get(id=event_id)
    event_serializer = EventSerializer(event, many=False)
    event_data = event_serializer.data
    event_data['start_date'] = str(datetime.strptime(event_data['start_date'], '%Y-%m-%d').date().strftime("%d.%m.%Y"))
    event_data['end_date'] = str(datetime.strptime(event_data['end_date'], '%Y-%m-%d').date().strftime("%d.%m.%Y"))
    context['event'] = event_data

    print(context)

    return render(request, 'main_pages/view_event.html', context)


@csrf_exempt
@login_required(login_url='/accounts/login/')
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

    if request.method == "POST":
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