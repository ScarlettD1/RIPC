let baseURL = `${document.location.protocol}//${document.location.host}`
let variantInfo = {}
let eventID = Number(document.location.href.split('/')[document.location.href.split('/').length-2])

$(document).ready(function(){
    getStartData()
});


// Создание заданий
async function createTasks() {
    $("#modal-view-cropping #text").text("Процесс создания заданий")
    $(".block-page").show()
    $("#modal-view-cropping").show()
    $.ajax({
        type: "GET",
        url: `${baseURL}/api/task?end_step=true&event=${eventID}`,
        success: function (jqXHR) {
        // Если успешно - отправить на новый шаг
            console.log("Задания созданы!");
            $("#modal-view-cropping #text").text("")
            $("#modal-view-cropping").hide()
            $(".block-page").hide()

            // Обновление страницы
            setTimeout(function(){
                window.location = window.location.href;
            }, 1000);

        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
            alert("Ошибка при создании заданий!")
            $("#modal-view-cropping #text").text("")
            $("#modal-view-cropping").hide()
            $(".block-page").hide()

            // Обновление страницы
            setTimeout(function(){
                window.location = window.location.href;
            }, 1000);
        }
    });
}


// Функция запуска обрезки заданий
async function startCroppingVar(variantID) {
    $("#modal-view-cropping #text").text("Процесс обрезки вариантов")
    $(".block-page").show()
    $("#modal-view-cropping").show()
    let resultCheck = Array(variantID.length).fill(false);
    for (let i in variantID) {
        let v_id = variantID[i]
        $.ajax({
            type: "GET",
            url: `${baseURL}/api/cropping_variant/start/${v_id}?update=true`,
            success: function (response) {
                console.log(`Обрезка заданий для варианта [${v_id}] завершена!`)
                resultCheck[i] = true

            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(`ERROR: Ошибка при обрезки заданий для варианта [${v_id}]!`)
                alert(`Ошибка при обрезки заданий для варианта [${v_id}]!`)
                $("#modal-view-cropping").hide()
                $(".block-page").hide()
                $("#modal-view-cropping #text").text("")
                return
            }
        });
    }

    let intervalId = setInterval(function () {
        if (resultCheck.every(element => element === true)) {
            clearInterval(intervalId)
            $("#modal-view-cropping").hide()
            $(".block-page").hide()
            $("#modal-view-cropping #text").text("")

            // Создание заданий
            createTasks()
        }
    }, 200);
}

// Функция запуска обрезки критериев
async function startCroppingCrit(criteriaID) {
    $("#modal-view-cropping #text").text("Процесс обрезки критериев")
    $(".block-page").show()
    $("#modal-view-cropping").show()
    let resultCheck = Array(criteriaID.length).fill(false);
    for (let i in criteriaID) {
        let c_id = criteriaID[i]
        $.ajax({
            type: "GET",
            url: `${baseURL}/api/cropping_criteria/start/${c_id}?update=true`,
            success: function (response) {
                console.log(`Обрезка критериев [${c_id}] завершена!`)
                resultCheck[i] = true
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(`ERROR: Ошибка при обрезки заданий для варианта [${v_id}]!`)
                alert(`Ошибка при обрезки заданий для варианта [${v_id}]!`)
                $("#modal-view-cropping").hide()
                $(".block-page").hide()
                $("#modal-view-cropping #text").text("")
                return
            }
        });
    }
    let intervalId = setInterval(function () {
        if (resultCheck.every(element => element === true)) {
            clearInterval(intervalId)
            $("#modal-view-cropping").hide()
            $(".block-page").hide()
            $("#modal-view-cropping #text").text("")

            // Создание заданий
            createTasks()
        }
    }, 200);
}


function getStartData() {
    let variantDiv = $("#startData #variantFiles").find('.startvar')
    for (let i=0; i<variantDiv.length; i++) {
        let variant = $(variantDiv[i])
        let varFileID = Number(variant.attr('id').split('-')[1])
        let varFilename = variant.find('#startvar-file_name').text()
        let criteria = $(variant.find('.startcrit'))
        let critID = Number(criteria.attr('id').split('-')[1])
        let critFilename = criteria.find('#startcrit-file_name').text()

        variantInfo[varFileID] = {
            "filename": varFilename,
            "criteria": {
                "id": critID,
                "filename": critFilename
            }
        }
    }
    $("#startData").remove()
}


// Функция для календаря
$('#inputCalendar .input-daterange').datepicker({
    format: "dd.mm.yyyy",
    language: "ru",
    orientation: "bottom right",
    autoclose: true,
    todayHighlight: true
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


$("#main-settings-form").submit(function (e) {
    e.preventDefault();
    let formData = {}

    // Получаем текстовые данные с формы
    $.each($(this).serializeArray(), function (key, value) {
        formData[value.name] = value.value
    })

    // Запрос на обновление МП
    $.ajax({
        type: "PUT",
        url: `${baseURL}/api/event/${eventID}`,
        data: JSON.stringify(formData),
        dataType: "json",
        success: function (response) {
            console.log("Основные настройкм мероприятия обновлены!");
            let filesData = new FormData();
            let hasFiles = false;

            // Получаем данные для обновления файлов
            let table_child = $('#main-settings-form table tbody').children()
            for (let i =0; i < table_child.length; i++) {
                let var_id = $(table_child[i]).attr('id').split('-')[1]
                let file = $(table_child[i]).find("input[name='new_variant_file']")[0].files[0]
                if (file) {
                    filesData.append(`${var_id}&&${file.name}`, file)
                    hasFiles = true
                }
            }
            if (!hasFiles) {
                // Обновление страницы
                setTimeout(function(){
                    window.location = window.location.href;
                }, 1000);
                return
            }
            // Запрос на обновление файлов варианта
            $.ajax({
                type: "POST",
                url: `${baseURL}/api/variant/?update=true`,
                enctype: 'multipart/form-data',
                processData: false,
                contentType: false,
                cache: false,
                data: filesData,
                success: function (response) {
                    let variantID = response;
                    console.log("Файлы для обновления вариантов отправлены!");
                    // Запуск обрезки заданий (Сёма)
                    startCroppingVar(variantID)

                },
                error: function(jqXHR, textStatus, errorThrown) {
                    console.log(textStatus, jqXHR.responseText);
                    alert("Ошибка при обновлении вариантов!")
                }
            })
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
            alert("Ошибка при обновлении основных настроек мероприятия!")
        }
    })
});


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

    // Запрос на обновление шаблонов заданий
    $.ajax({
        type: "PUT",
        url: `${baseURL}/api/pattern_task/`,
        data: JSON.stringify(data),
        dataType: "JSON",
        success: function (jqXHR) {
            console.log("Настройки шаблонов обновлены!");
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
            alert("Ошибка при обновлении шаблонов!")
        }
    });
});


// Обновление файлов критерий
$("#matching-criteria-form").submit(function (e) {
    e.preventDefault();
    let data = new FormData();

    let table_child = $('#matching-criteria-form table tbody').children()
    for (let i =0; i < table_child.length; i++) {
        let var_id = $(table_child[i]).attr('id').split('-')[1]
        let crit_id = $($(table_child[i]).find(".btn-danger")[0]).attr('id')
        let file = $(table_child[i]).find("input[name='new_criteria_file']")[0].files[0]

        data.append(`${crit_id}&&${var_id}`, file)
    }

    $.ajax({
        type: "POST",
        url: `${baseURL}/api/criteria/?update=true`,
        enctype: 'multipart/form-data',
        processData: false,
        contentType: false,
        cache: false,
        data: data,
        success: function (response) {
            let criteriaID = response;
            console.log("Файлы для обновления критериев отправлены!");
            // Запуск обрезки критериев (Сёма)
            startCroppingCrit(criteriaID)

        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
            alert("Ошибка при обновлении критериев!")
        }
    });
});


// Отслеживание нажатий на показ файла варианта
$('#main-settings-form table .btn-success').click(function (e) {
    e.preventDefault();
    let file_id = $(this).attr('id')
    let file_url = `/api/variant/file/${file_id}`
    $('.block-page #modal-view-file iframe').attr('id', `pdf-${file_id}`).attr('src', file_url)
    $('.block-page').show();
    $('#modal-view-file').show();
});


// Отслеживание нажатий на показ файла критериев
$('#matching-criteria-form table .btn-danger').click(function (e) {
    e.preventDefault();
    let file_id = $(this).attr('id')
    let file_url = `/api/criteria/file/${file_id}`
    $('.block-page #modal-view-file iframe').attr('id', `pdf-${file_id}`).attr('src', file_url)
    $('.block-page').show();
    $('#modal-view-file').show();
});


// Закрыть модальное окно показа файлов
$('#modal-view-file #close-modal').click(function(){
    $('.block-page #modal-view-file iframe').attr('id', `pdf-0`).attr('src', '')
    $('.block-page').hide();
    $('#modal-view-file').hide();
});




