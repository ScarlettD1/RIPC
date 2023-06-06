let baseURL = `${document.location.protocol}//${document.location.host}`
let variantInfo = {}
let eventID = Number(document.location.href.split('/')[document.location.href.split('/').length-2])

$(document).ready(function(){
    getStartData()
});


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




