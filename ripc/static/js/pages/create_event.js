let subjects = {} // Данные учебных дисциплин
let baseURL = "http://127.0.0.1:8000"
let eventID = 0
let variantID = []
let patternID = []
let croppingID = []
let croppingEnd = false
let matchingCropping = []
let currentMatchingIndex = 0

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
    format: "dd.mm.yyyy",
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


// Функция запуска обрезки заданий
async function startCropping() {
    for (let i in variantID) {
        let v_id = variantID[i]
        $.ajax({
            type: "GET",
            url: `${baseURL}/api/cropping_variant/start/${v_id}`,
            success: function (response) {
                console.log(`Обрезка заданий для варианта [${v_id}] завершена!`)
                for (let res_i in response)
                    croppingID.push([v_id , response[res_i]])
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(`ERROR: Ошибка при обрезки заданий для варианта [${v_id}]!`)
                alert(`Ошибка при обрезки заданий для варианта [${v_id}]!`)
            }
        });
    }
    croppingEnd = true;
}


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
        url: `${baseURL}/api/event/`,
        data: JSON.stringify(formData),
        dataType: "json"
    }).fail(function (){
        console.log('error: Не удалось отправить основные настройки')
        alert("Ошибка при отправке основных настроек!")
    })

    // Запрос на создание файлов варианта
    let res_files = $.ajax({
        type: "POST",
        url: `${baseURL}/api/variant/`,
        enctype: 'multipart/form-data',
        processData: false,
        contentType: false,
        cache: false,
        data: filesData
    }).fail(function (){
        console.log('error: Не удалось отправить файлы вариантов')
        alert("Ошибка при отправке файлов вариантов!")
    });

    // Если все запросы выполнились - перейти на следующий шаг
    $.when(res_event, res_files).done(function (){
        eventID = res_event.responseJSON;
        variantID = res_files.responseJSON;
        console.log("ok: Основные настройки отправлены!");
        $('.page-block .main-settings .head .btn').click();
        $('.page-block .main-settings #main-settings-form .btn').remove();
        $('.page-block .templates-settings').show().trigger('show');
        $('.page-block .main-settings #main-settings-form').find('input').attr('readonly', true);

        // Запуск обрезки заданий (Сёма)
        startCropping()
    })
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
                $('.table #task-1 #inputEventSubject').append(`<option value=${response[i].id}>${response[i].name}</option>`)
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
            alert("Ошибка при получении предметных областей!")
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
        <tr id=task-${count_rows+1}>
            <td><input class="checkbox w-100" type="checkbox"></td>
            <td style="width: 50px;"><input name="task_num" class="w-100" type="number" readonly="readonly" required value=${count_rows+1}></td>
            <td>
                <select name="subject" class="w-100" id="inputEventSubject" required>
                    <option disabled>Предметная область</option>
                    ${options}
                </select>
            </td>
            <td><input name="max_score" class="w-100" id="inputEventMaxScore" type="number" min="0" required></td>
            <td><input name="check_times" class="w-100" id="inputCheckTime" type="number" min="1" required></td>
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
    for (let i=0; i<form.length; i+=4){
        let temp = {}
        temp[form[i].name] = form[i].value
        temp[form[i+1].name] = form[i+1].value
        temp[form[i+2].name] = form[i+2].value
        temp[form[i+3].name] = form[i+2].value
        data.push(temp);
    }

    $.ajax({
        type: "POST",
        url: `${baseURL}/api/pattern_task/`,
        data: JSON.stringify(data),
        dataType: "JSON",
        success: function (jqXHR) {
        // Если успешно - отправить на новый шаг
            console.log("Настройки шаблонов отправлены!");
            patternID = jqXHR
            $('.page-block .templates-settings .head .btn').click();
            $('.page-block .templates-settings #templates-settings-form .btn').remove();
            $('.page-block .templates-settings #templates-settings-form').find('input').attr('readonly', true);
            $('.page-block .templates-settings #templates-settings-form').find('select').attr('disabled', true);
            $('.page-block .matching-criteria').show().trigger('show');
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
            alert("Ошибка при отправки шаблонов!")
        }
    });
});


// Заполнение выбора шаблонов
$('.page-block .matching-criteria').on('show', function(){
    $.ajax({
        type: "GET",
        url: `${baseURL}/api/variant/?id=${variantID}`,
        success: function (response) {
            console.log("Варианты получены!")
            // Заполнение полученными данными
            if (response instanceof Array) {
                for (let i=0; i<response.length; i++){
                    let file_split = response[i].file_path.split('&&')
                    let file_name = file_split[file_split.length-1]
                    $('.page-block .matching-criteria .table tbody').append(`
                        <tr id=variant-${response[i].id}>
                            <td><input name="variant_name" class="w-100" type="text" required readonly="readonly" value='${file_name}'></td>
                            <td><input name="criteria_file" type="file" accept="application/pdf" required></td>
                        </tr>
                    `)
                }
                return
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
            alert("Ошибка при получении предметных областей!")
        }
    });
});


// Отправка настроек сопоставлений
$("#matching-criteria-form").submit(function (e) {
    e.preventDefault();
    let data = new FormData();

    let table_child = $('#matching-criteria-form table tbody').children()
    for (let i =0; i < table_child.length; i++) {
        let var_id = $(table_child[i]).attr('id').split('-')[1]
        let file = $(table_child[i]).find("input[name='criteria_file']")[0].files[0]

        data.append(var_id, file)
    }

    $.ajax({
        type: "POST",
        url: `${baseURL}/api/criteria/`,
        enctype: 'multipart/form-data',
        processData: false,
        contentType: false,
        cache: false,
        data: data,
        success: function (jqXHR) {
            // Если успешно - отправить на новый шаг
            console.log("Критерии отправлены!");
            patternID = jqXHR
            $('.page-block .matching-criteria .head .btn').click();
            $('.page-block .matching-criteria #matching-criteria-form-form .btn').remove();
            $('.page-block .matching-criteria #matching-criteria-form').find('input').attr('readonly', true);

            // Перейти на страницу добавления организаций
            // setTimeout(function(){
            //     window.location.href = `${baseURL}/event_organization/${eventID}`;
            // }, 1000);

        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
            alert("Ошибка при сопоставлении!")
        }
    });
});
