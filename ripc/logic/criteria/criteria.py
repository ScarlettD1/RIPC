from time import time

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ripc.logic.required import region_rep_required


@csrf_exempt
@login_required(login_url='/accounts/login/')
@region_rep_required(login_url='/accounts/login/')
def criteria_api(request):
    if request.method == "POST":
        datas = []
        for name, file in request.FILES.items():
            file_path = f'File_Storage/criteria/{int(time())}&&criteria_for_{name}.pdf'
            with open(file_path, "wb") as new_file:
                new_file.write(file.read())
            datas.append({"variant": name, "file_path": file_path})

        # variant_ids = []
        # for data in datas:
        #     variants_serializer = VariantSerializer(data=data)
        #     if not variants_serializer.is_valid():
        #         return JsonResponse("ERROR", status=400, safe=False)
        #     variants_serializer.save()
        #     variant_ids.append(variants_serializer.data.get('id'))
        # return JsonResponse(variant_ids, status=200, safe=False)

    return JsonResponse("ERROR", status=400, safe=False)
