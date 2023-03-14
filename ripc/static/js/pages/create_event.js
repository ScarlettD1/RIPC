$('#inputCalendar .input-daterange').datepicker({
    format: "dd/mm/yyyy",
    language: "ru",
    orientation: "bottom right",
    autoclose: true,
    todayHighlight: true
});

$("#inputEventFiles").fileinput({
    theme: "fa5",
    language: "ru",
    uploadUrl: "/",
    uploadAsync: true,
    allowedFileExtensions: ["pdf"],
    removeFromPreviewOnError: true,
    browseClass: "btn btn-info",
    mainClass: "d-grid w-75",
    showClose: false,
    showUpload: false,
    enableResumableUpload: true,
    initialPreviewAsData: true,
    preferIconicPreview: true,
    previewFileIcon: '<i class="fas fa-file"></i>',
    previewFileIconSettings: {
        'pdf': '<i class="fas fa-file-pdf text-danger"></i>',
    },
    fileActionSettings: {
        showZoom: false
    }
});