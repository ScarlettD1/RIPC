from time import time
import PyPDF2

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, FileResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from ripc.logic.required import region_resp_required
from ripc.logic.smtp.smtp import Smtp
from ripc.models import Variant, Event, OrganizationRep, OrganizationEvent, Complect
from ripc.serializers import VariantSerializer

baseURL = "http://127.0.0.1:8000"


@csrf_exempt
@xframe_options_exempt
@login_required(login_url='/accounts/login/')
@region_resp_required(login_url='/accounts/login/')
def variant_api_file(request, id=0):
    if request.method == "GET":
        if id:
            variants = Variant.objects.get(id=id)
            variants_serializer = VariantSerializer(variants, many=False)
            file_path = variants_serializer['file_path'].value
            file_name = file_path.split('&&')[-1]
            return FileResponse(open(file_path, "rb"), as_attachment=False, filename=file_name)

    return JsonResponse("ERROR", status=400, safe=False)


@csrf_exempt
@login_required(login_url='/accounts/login/')
@region_resp_required(login_url='/accounts/login/')
def variant_api(request):
    if request.method == "POST" and request.GET.get('update'):
        variant_ids = []
        if not request.FILES:
            return JsonResponse(variant_ids, status=200, safe=False)

        event_id = 0
        for name, file in request.FILES.items():
            var_id = name.split('&&')[0]
            old_variant = Variant.objects.get(id=var_id)
            event_id = old_variant.event_id

            filename = name.split('&&')[1]
            file_path = f'File_Storage/variant/{int(time())}&&{filename}'
            with open(file_path, "wb") as new_file:
                new_file.write(file.read())
            # Считываем PDF для подсчёта страниц
            reader = PyPDF2.PdfReader(file_path)
            data = {"page_count": str(len(reader.pages)), "file_path": file_path, "event": event_id}

            variants_serializer = VariantSerializer(old_variant, data=data)
            if not variants_serializer.is_valid():
                print(variants_serializer.errors)
                return JsonResponse("ERROR", status=400, safe=False)
            variants_serializer.save()
            variant_ids.append(var_id)

        # Удаление комплектов в мероприятиях
        event_organizations = OrganizationEvent.objects.filter(event=event_id)
        for event_organization in event_organizations:
            Complect.objects.filter(organization_event=event_organization.id).delete()


        # Отправить расслыку ответсенным организаций
        event = Event.objects.get(id=event_id)
        for event_organization in event_organizations:
            org_resps = OrganizationRep.objects.filter(organization=event_organization.organization.id)
            org_resp_users_email = []
            for org_resp in org_resps:
                org_resp_users_email.append(User.objects.get(id=org_resp.user_id).email)
            smtp = Smtp()
            smtp.send_mail(
                subject="Изменения в мероприятии",
                to_addr=org_resp_users_email,
                text=f"""
                Здравствуйте,
                Для мероприятия "{event.name}" изменились варинаты.
    
                Вам требуется перегенерировать необходимое количество комплектов.
                Ссылка: {baseURL}/event/{event.id}/
    
                С уважением,
                Команда RIPC.
                """
            )
        return JsonResponse(variant_ids, status=200, safe=False)

    if request.method == "POST":
        datas = []
        event_id = request.POST['event_id']
        for name, file in request.FILES.items():
            file_path = f'File_Storage/variant/{int(time())}&&{name}'
            with open(file_path, "wb") as new_file:
                new_file.write(file.read())
            # Считываем PDF для подсчёта страниц
            reader = PyPDF2.PdfReader(file_path)
            datas.append({"page_count": str(len(reader.pages)), "file_path": file_path, "event": event_id})

        variant_ids = []
        for data in datas:
            variants_serializer = VariantSerializer(data=data)
            if not variants_serializer.is_valid():
                return JsonResponse("ERROR", status=400, safe=False)
            variants_serializer.save()
            variant_ids.append(variants_serializer.data.get('id'))
        return JsonResponse(variant_ids, status=200, safe=False)

    if request.method == "GET":
        query = {}
        # Поиск query
        ids = request.GET.get('id')
        if ids and len(ids.split(',')) > 1:
            ids = ids.split(',')
        event_ids = request.GET.get('event_id')
        if event_ids and len(event_ids.split(',')) > 1:
            event_ids = event_ids.split(',')

        if ids:
            query['id__in'] = ids if type(ids) is list else [ids]

        if event_ids:
            query['event__in'] = event_ids if type(event_ids) is list else [event_ids]

        if query:
            patterns = Variant.objects.filter(**query)
            patterns_serializer = VariantSerializer(patterns, many=True)
            return JsonResponse(patterns_serializer.data, status=200, safe=False)

    return JsonResponse("ERROR", status=400, safe=False)
