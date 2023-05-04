let subjects = {} // Данные учебных дисциплин
let baseURL = "http://127.0.0.1:8000"
let eventID = 0
let variantID = []
let patternID = []

$(document).ready(function(){
    // $('.page-block .main-settings .head .btn').click();
    // $('.page-block .main-settings #main-settings-form .btn').remove();
    // $('.page-block .templates-settings').show().trigger('show');
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
    let formData = {}
    let filesData = new FormData();

    // Получаем текстовые данные с формы
    $.each($(this).serializeArray(),function (key, value) {
        formData[value.name] = value.value
    })

    // Получаем файлы с формы
    $.each($(this).find('#inputEventFiles')[0].files, function (key, value) {
        filesData.append(value.name, value);
	})

    // Запрос на создание МП
    let res_event = $.ajax({
        type: "POST",
        url: `${baseURL}/api/event`,
        data: JSON.stringify(formData),
        dataType: "json"
    }).fail(function (){
        console.log('error: Не удалось отправить основные настройки')
    })

    // Запрос на создание файлов варианта
    let res_files = $.ajax({
        type: "POST",
        url: `${baseURL}/api/variant`,
        enctype: 'multipart/form-data',
        processData: false,
        contentType: false,
        cache: false,
        data: filesData
    }).fail(function (){
        console.log('error: Не удалось отправить файлы вариантов')
    });

    // Если все запросы выполнились - перейти на следующий шаг
    $.when(res_event, res_files).done(function (data){
        eventID = res_event.responseJSON;
        variantID = res_files.responseJSON;
        console.log("ok: Основные настройки отправлены!");
        $('.page-block .main-settings .head .btn').click();
        $('.page-block .main-settings #main-settings-form .btn').remove();
        $('.page-block .templates-settings').show().trigger('show');
        $('.page-block .main-settings #main-settings-form').find('input').attr('readonly', true);
    });
});


// Заполнение предметных областей
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
                $('.table #1 #inputEventSubject').append(`<option value=${response[i].id}>${response[i].name}</option>`)
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
        }
    });
});


// Добавление нового поля в настройке шаблонов
$('.page-block .templates-settings .create-event-form .btn-toolbar .btn-primary').click(function(){
    let table_rows = $(this).parent().parent().find('.table').find('tbody')
    let count_rows = table_rows.children().length

    // Заполнение предметных областей
    let options = ''
    for (let id in subjects){
        options += `<option value=${id}>${subjects[id]}</option>`
    }

    // Добавление поля
    table_rows.append(`
        <tr id=${count_rows+1}>
            <td><input class="checkbox w-100" type="checkbox"></td>
            <td>
                <select name="subject_id" class="w-100" id="inputEventSubject" required>
                    <option disabled>Предметная область</option>
                    ${options}
                </select>
            </td>
            <td><input name="max_score" class="w-100" id="inputEventMaxScore" type="number" min="0" required></td>
            <td><input name="name" class="w-100" id="inputEventTemplateName" type="text" required></td>
        </tr>
    `)
});


// Удаление выделенных полей в настройке шаблонов
$('.page-block .templates-settings .create-event-form .btn-toolbar .btn-danger').click(function(){
    let table_rows = $(this).parent().parent().find('.table').find('tbody')
    let rows = table_rows.children('tr')

    $(rows).each(function (){
        if ($(this).find('.checkbox').is(':checked')){
            $(this).remove()
        }
    });
});

// Отправка настроек шаблона
$("#templates-settings-form").submit(function (e) {
    e.preventDefault();
    let form = $(this).serializeArray()
    let data = []
    for (let i=0; i<form.length; i+=3){
        let temp = {}
        temp[form[i].name] = form[i].value
        temp[form[i+1].name] = form[i+1].value
        temp[form[i+2].name] = form[i+2].value
        data.push(temp);
    }

    $.ajax({
        type: "POST",
        url: `${baseURL}/api/pattern_task`,
        data: JSON.stringify(data),
        dataType: "JSON",
        success: function (jqXHR) {
        // Если успешно - отправить на новый шаг
            console.log("Настройки шаблонов отправлены!");
            patternID = jqXHR
            $('.page-block .templates-settings .head .btn').click();
            $('.page-block .templates-settings #templates-settings-form .btn').remove();
            $('.page-block .matching-templates').show().trigger('show');
            $('.page-block .templates-settings #templates-settings-form').find('input').attr('readonly', true);
            $('.page-block .templates-settings #templates-settings-form').find('select').attr('disabled', true);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
        }
    });
});