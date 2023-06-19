from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.views.decorators.csrf import csrf_exempt

from ripc.logic.required import some_resp_required


@csrf_exempt
@login_required(login_url='/accounts/login/')
@some_resp_required(login_url='/accounts/login/')
def scanner_download(request):
    if request.method == "GET":
        context = {}
        return FileResponse(open('File_Storage/scanner/setup.msi', "rb"), as_attachment=True, filename='RIPC Scanner Setup.msi')
