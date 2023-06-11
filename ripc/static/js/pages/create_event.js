let subjects = {} // Данные учебных дисциплин
let baseURL = `${document.location.protocol}//${document.location.host}`
let eventID = 0
let variantID = []
let patternID = []
let croppingID = []
let fileinputOptions = {
    theme: "fa5",
    language: "ru",
    uploadUrl: '/',
    uploadAsync: false,
    allowedFileExtensions: ["pdf"],
    removeFromPreviewOnError: true,
    browseClass: "btn btn-info",
    mainClass: "d-grid w-75",
    autoUpload: false,
    showClose: false,
    showUpload: false,
    enableResumableUpload: true,
    preferIconicPreview: true,
    initialPreview: [],
    initialPreviewConfig: [],
    previewFileIconSettings: {
        'pdf': '<i class="fas fa-file-pdf text-danger"></i>',
    },
    fileActionSettings: {
        showZoom: true,
        indicatorNew: ''
    }
}

$(document).ready(function(){
    // Функция для календаря
    $('#inputCalendar .input-daterange').datepicker({
        format: "dd.mm.yyyy",
        language: "ru",
        orientation: "bottom right",
        autoclose: true,
        todayHighlight: true
    });

    getStartData().then(function () {
        // Функция для файлов
        $("#inputEventFiles").fileinput(fileinputOptions);
        if (variantID) {
            $('.file-actions .file-footer-buttons .kv-file-remove').remove();
            $('.file-actions .file-footer-buttons .kv-file-zoom').prop('disabled', false);
        }
    });
});


async function getStartData() {
    let event = Number($("#startData #event_id").text())
    if (!event){
        return
    }
    $("#startData").remove()

    eventID = event
    let completed = true;

    await $.ajax({
        type: "GET",
        url: `${baseURL}/api/event/?id=${eventID}`,
        dataType: 'JSON',
        success: function (response) {
            console.log("Основные настройки получены!")
            $("#main-settings-form #inputEventName").val(response["name"])
            $("#main-settings-form #inputEventStartDate").val(response["start_date"])
            $("#main-settings-form #inputEventEndDate").val(response["end_date"])

            $('#inputCalendar .input-daterange').datepicker({}).on('show', function (e) {
                $('.day').click(function (event) {
                    event.preventDefault();
                    event.stopPropagation();
                });
            });
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
            alert("Ошибка при получении основных настроек!")
            completed = false
            return
        }
    });
    if (!completed) return;
    await $.ajax({
        type: "GET",
        url: `${baseURL}/api/variant/?event_id=${eventID}`,
        dataType: 'JSON',
        success: function (response) {
            console.log("Варианты получены!")
            fileinputOptions["initialPreviewAsData"] = false
            for (let i = 0; i < response.length; i++) {
                variantID.push(response[i]["id"])
                fileinputOptions['initialPreview'].push(`<iframe class="kv-preview-data" src="${baseURL}/api/variant/file/${response[i]['id']}"></iframe>`)
                fileinputOptions['initialPreviewConfig'].push({
                    type: "pdf",
                    caption: response[i]['file_path'].split('&&')[response[i]['file_path'].split('&&').length-1],
                    key: i+1,
                    previewAsData: false,
                })
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log("Ошибка при получении вариантов!");
            completed = false
            return
        }
    });
    if (!completed) return;
    console.log("ok: Этап 1!");
    $('.page-block .main-settings .head .btn').click();
    $('.page-block .main-settings #main-settings-form .btn').remove();
    $('.page-block .main-settings #main-settings-form').find('input').attr('readonly', true);

    completed = await $.ajax({
        type: "GET",
        url: `${baseURL}/api/subject`,
        dataType: 'JSON',
        success: function (response) {
            console.log("Предметные области получены!")
            // Заполнение полученными данными
            for (let i=0; i<response.length; i++){
                subjects[response[i].id] = response[i].name
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
            alert("Ошибка при получении предметных областей!")
            completed = false
            return
        }
    });
    if (!completed) return;
    $('.page-block .templates-settings').show()

    await $.ajax({
        type: "GET",
        url: `${baseURL}/api/pattern_task/?event_id=${eventID}`,
        dataType: 'JSON',
        success: function (response) {
            if (!response.length) {
                console.log("Настройки шаблонов вариантов не получены!")
                $('.page-block .templates-settings').trigger("show")
                 completed = false
                return
            }
            console.log("Настройки шаблонов вариантов получены!")
            let table_rows = $("#templates-settings-form table tbody")
            table_rows.children().remove()

            for (let i = 0; i < response.length; i++) {
                patternID.push(response[i]["id"])
                // Заполнение предметных областей
                let options = ''
                for (let id in subjects){
                    if (id === response[i]["subject"]) {
                        options += `<option selected value=${id}>${subjects[id]}</option>`
                    }
                    else {
                        options += `<option value=${id}>${subjects[id]}</option>`
                    }

                }
                // Добавление поля
                table_rows.append(`
                    <tr id=task-${response[i]["task_num"]}>
                        <td><input class="checkbox w-100" type="checkbox"></td>
                        <td style="width: 50px;"><input name="task_num" class="w-100" type="number" readonly="readonly" required value=${response[i]["task_num"]}></td>
                        <td>
                            <select name="subject" class="w-100" id="inputEventSubject" required>
                                <option disabled>Предметная область</option>
                                ${options}
                            </select>
                        </td>
                        <td><input name="max_score" class="w-100" id="inputEventMaxScore" type="number" min="0" required value="${response[i]["max_score"]}"></td>
                        <td><input name="check_times" class="w-100" id="inputCheckTime" type="number" min="1" required value="${response[i]["check_times"]}"></td>
                    </tr>
                `)
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log("Ошибка при получении настроек шаблонов вариантов!")
            completed = false
            return
        }
    });
    if (!completed) return;
    console.log("ok: Этап 2!");
    $('.page-block .templates-settings .head .btn').click();
    $('.page-block .templates-settings #templates-settings-form .btn').remove();
    $('.page-block .templates-settings #templates-settings-form').find('input').attr('readonly', true);
    $('.page-block .templates-settings #templates-settings-form').find('select').attr('disabled', true);
    $('.page-block .matching-criteria').show().trigger('show');
}


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
    let files = $("#inputEventFiles").fileinput("getFileStack");
    for (let name in files) {
        filesData.append(files[name]["name"], files[name]["file"]);
    }

    // Запрос на создание МП
    $.ajax({
        type: "POST",
        url: `${baseURL}/api/event/`,
        data: JSON.stringify(formData),
        dataType: "json",
        success: function (response) {
            eventID = response
            filesData.append('event_id', eventID);

            // Запрос на создание файлов варианта
            $.ajax({
                type: "POST",
                url: `${baseURL}/api/variant/`,
                enctype: 'multipart/form-data',
                processData: false,
                contentType: false,
                cache: false,
                data: filesData,
                success: function (response) {
                    variantID = response;
                    console.log("ok: Основные настройки отправлены!");
                    // $('.page-block .main-settings .head .btn').click();
                    $('.page-block .main-settings #main-settings-form .btn').remove();
                    // $('.page-block .templates-settings').show().trigger('show');
                    $('.page-block .main-settings #main-settings-form').find('input').attr('readonly', true);
                    $('#inputCalendar .input-daterange').datepicker({
                        }).on('show', function(e){
                            $('.day').click(function(event) {
                                event.preventDefault();
                                event.stopPropagation();
                        });
                    });
                    $('.file-actions .file-footer-buttons .kv-file-remove').remove();
                    $('.file-actions .file-footer-buttons .kv-file-zoom').prop('disabled', false);

                    // Запуск обрезки заданий (Сёма)
                    startCropping()
                    setTimeout(function(){
                        window.location.href = `${baseURL}/event_organization/${eventID}`;
                    }, 1000);
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    console.log(textStatus, jqXHR.responseText);
                    alert("Ошибка при обработке файлов варинатов!")
                }
            })
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
            alert("Ошибка при создании мероприятия!")
        }
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
        temp[form[i+3].name] = form[i+3].value
        temp['event'] = eventID
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
            setTimeout(function(){
                window.location.href = `${baseURL}/event_organization/${eventID}`;
            }, 1000);

        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
            alert("Ошибка при сопоставлении!")
        }
    });
});
