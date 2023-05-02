let subjects = {} // Данные учебных дисциплин
let baseURL = "http://127.0.0.1:8000"

$(document).ready(function(){

});

// Отслеживание нажатий на скрытие/показ
$('.page-block .head .btn').click(function(){
    let mainParent = $(this).parent().parent()
    let mainChildren = mainParent.children().not('.head')

    // Скрытие/показ детей
    if ($(mainChildren).is(':hidden')) {
        $(mainChildren).show()
        $(this).find('i').attr("class", "fas fa-chevron-down")
    }
    else {
        $(mainChildren).hide()
        $(this).find('i').attr("class", "fas fa-chevron-right")
    }

});

// Функция для календаря
$('#inputCalendar .input-daterange').datepicker({
    format: "dd/mm/yyyy",
    language: "ru",
    orientation: "bottom right",
    autoclose: true,
    todayHighlight: true
});

// Функция для файлов
$("#inputEventFiles").fileinput({
    theme: "fa5",
    language: "ru",
    allowedFileExtensions: ["pdf"],
    removeFromPreviewOnError: true,
    browseClass: "btn btn-info",
    mainClass: "d-grid w-75",
    showClose: false,
    showUpload: false,
    enableResumableUpload: true,
    initialPreviewAsData: true,
    preferIconicPreview: true,
    previewFileIconSettings: {
        'pdf': '<i class="fas fa-file-pdf text-danger"></i>',
    },
    fileActionSettings: {
        showZoom: false,
        indicatorNew: ''
    }
});

// Отправка главных настроек
$("#main-settings-form").submit(function (e) {
    e.preventDefault();
    let formData = new FormData();

    // Получаем текстовые данные с формы
    $.each($(this).serializeArray(),function (key, value) {
        formData.append(value.name, value.value);
    })

    // Получаем файлы с формы
    $.each($(this).find('#inputEventFiles')[0].files, function (key, value) {
        formData.append("files[]", value, value.name);
	})

    $.ajax({
        type: "POST",
        url: "https://webhook.site/728a2b8c-145f-4367-9de6-c647a227ea2d",
        processData: false,
        contentType: false,
        data: formData,
        success: function (jqXHR) {
        // Если успешно - отправить на новый шаг
            console.log("Основные настройки отправлены!");
            $('.page-block .main-settings .head .btn').click();
            $('.page-block .main-settings #main-settings-form .btn').remove();
            $('.page-block .templates-settings').show().trigger('show');
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
            $('.page-block .main-settings .head .btn').click();
            $('.page-block .main-settings #main-settings-form .btn').remove();
            $('.page-block .templates-settings').show().trigger('show');
        }
    });
});


$('.page-block .templates-settings').on('show', function(){

    $.ajax({
        type: "GET",
        url: `${baseURL}/api/subject`,
        dataType: 'JSON',
        success: function (response) {
            console.log("Предметные области получены!")
            // Заполнение полученными данными
            for (let i=0; i<response.length; i++){
                subjects[response[i].id] = response[i].name
                $('#inputEventSubject').append(`<option value=${response[i].id}>${response[i].name}</option>`)
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
        }
    });
});