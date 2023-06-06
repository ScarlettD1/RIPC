from time import time

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from ripc.logic.required import region_resp_required
from ripc.models import Criteria
from ripc.serializers import CriteriaSerializer


@csrf_exempt
@xframe_options_exempt
@login_required(login_url='/accounts/login/')
@region_resp_required(login_url='/accounts/login/')
def criteria_api_file(request, id=0):
    if request.method == "GET":
        if id:
            criteria = Criteria.objects.get(id=id)
            criteria_serializer = CriteriaSerializer(criteria, many=False)
            file_path = criteria_serializer['file_path'].value
            file_name = file_path.split('&&')[-1]
            return FileResponse(open(file_path, "rb"), as_attachment=False, filename=file_name)

    return JsonResponse("ERROR", status=400, safe=False)



@csrf_exempt
@login_required(login_url='/accounts/login/')
@region_resp_required(login_url='/accounts/login/')
def criteria_api(request):
    if request.method == "POST":
        datas = []
        for name, file in request.FILES.items():
            file_path = f'File_Storage/criteria/{int(time())}&&criteria_for_{name}.pdf'
            with open(file_path, "wb") as new_file:
                new_file.write(file.read())
            datas.append({"variant": name, "file_path": file_path})

        criteria_ids = []
        for data in datas:
            criteria_serializer = CriteriaSerializer(data=data)
            if not criteria_serializer.is_valid():
                return JsonResponse("ERROR", status=400, safe=False)
            criteria_serializer.save()
            criteria_ids.append(criteria_serializer.data.get('id'))
            # Обрезка критериев + запись обрезанных (либо подавать байты изображения и потом сохранять) (Сёма)

        return JsonResponse(criteria_ids, status=200, safe=False)

    return JsonResponse("ERROR", status=400, safe=False)
