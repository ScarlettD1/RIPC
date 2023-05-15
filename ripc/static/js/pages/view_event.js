let baseURL = "http://127.0.0.1:8000"
let event_id = 0
let organization_id = 0
let scannedData = {}
let onlyNotScanned = false
let numberParticipants = 0

$(document).ready(function(){
    getStartData();
    updatePageData();
    setInterval(updatePageData, 5000);
});

function getStartData() {
    event_id = Number($('#startData #event_id')[0].innerText)
    organization_id = Number($('#startData #organization_id')[0].innerText)
    $('#startData').remove();
}

// Обновления данных на странице
async function updatePageData() {
    // Обновляем основную информацию
     await $.ajax({
        type: "GET",
        url: `${baseURL}/api/event_organization/?event_id=${event_id}&organization_id=${organization_id}`,
        success: function (response) {
            let data = response[0]
            $('header #percent_status').text(`Завершено на: ${data['percent_status']}%`);
            $('header #number_participants').text(`Кол-во участников: ${data['number_participants']}`);
            numberParticipants = data['number_participants']
            checkNumberParticipants()
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
        }
    });

    await $.ajax({
        type: "GET",
        url: `${baseURL}/api/complect_scan/?event_id=${event_id}&organization_id=${organization_id}`,
        success: function (response) {
            scannedData = response
            // Заполнение нераспознанных страниц
            let notRecognized = ''
            for (let i in scannedData['error_scanned_page']) {
                let page = scannedData['error_scanned_page'][i]
                notRecognized += `
                    <button class="blank btn btn-danger icon-button" id="page-${page['id']}">
                        <i class="bi bi-file-earmark-text-fill"></i>
                    </button>
                `;
            }
            $('.page-block .not-recognized h5').html(`Нераспознанные бланки: ${scannedData['error_scanned_page'].length}`);
            $('.page-block .not-recognized #not-recognized').html(notRecognized);
            $('.page-block .not-recognized #not-recognized .btn-danger').bind('click', view_not_recognized_modal);

            // Заполнение компплектов
            let recognized1 = '';
            let recognized2 = '';
            let recognized3 = '';
            let recognized4 = '';
            let count = 1;
            for (let i in scannedData['complect']) {
                let pages = scannedData['complect'][i];
                let pages_data = '';
                let page_number = 0;
                let all_scanned = true;
                for (let j in pages) {
                    page_number += 1;
                    let page = pages[j];
                    if (page.length === 0) {
                        all_scanned = false;
                        pages_data += `
                            <button class="btn btn-secondary num-button">
                                ${page_number}
                            </button>
                        `;
                    }
                    else {
                        pages_data += `
                            <button class="btn btn-success num-button" id="page-${page['id']}">
                                ${page_number}
                            </button>
                        `;
                    }
                }
                let complect_data = '';
                if (all_scanned) {
                    if (!onlyNotScanned){
                        complect_data = `
                            <div class="complect" id="complect-${i}">
                                <button class="btn btn-success icon-button" id="allpages-${i}" title="Комплект: №${i}">
                                    <i class="bi bi-justify-left"></i>
                                </button>
                                ${pages_data}
                            </div>
                        `;
                    }
                    else {
                        continue;
                    }
                }
                else {
                    complect_data = `
                        <div class="complect" id="complect-${i}">
                            <button class="btn btn-secondary icon-button" title="Комплект: №${i}">
                                <i class="bi bi-justify-left"></i>
                            </button>
                            ${pages_data}
                        </div>
                    `;
                }

                switch(count % 4) {
                    case 1:
                        recognized1 += complect_data
                        break;
                    case 2:
                        recognized2 += complect_data
                        break;
                    case 3:
                        recognized3 += complect_data
                        break;
                    case 0:
                        recognized4 += complect_data
                        break;
                }
                count += 1;
            }
            $('.page-block .recognized #list-1').html(recognized1);
            $('.page-block .recognized #list-2').html(recognized2);
            $('.page-block .recognized #list-3').html(recognized3);
            $('.page-block .recognized #list-4').html(recognized4);

            $('.page-block .recognized #recognized .btn-success[id^=\'page-\']').bind('click', view_recognized_modal);
            $('.page-block .recognized #recognized .btn-success[id^=\'allpages-\']').bind('click', view_recognized_modal);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
        }
    });
}


// Проверка нужно ли указать кол-во участников
function checkNumberParticipants() {
   if (numberParticipants === '0') {
        $('.block-page').show();
        $('#modal-view-number-participants').show();
        // Запуск генерации комплектов (Сёма)
   }
}

// Обновить кол-во участников
$('#modal-view-number-participants form').submit(function (e) {
    e.preventDefault();
    let number_participants = $(this).serializeArray()[0].value

     let data = {
        "event": event_id,
        "organization": organization_id,
        "number_participants": number_participants
    }
     $.ajax({
         type: "PUT",
         url: `${baseURL}/api/event_organization/`,
         data: JSON.stringify(data),
         dataType: "JSON",
         success: function (jqXHR) {
             console.log("Количество участников установлено")
             $('.block-page').hide();
             $('#modal-view-number-participants').hide();
         },
         error: function (jqXHR, textStatus, errorThrown) {
             console.log(textStatus, jqXHR.responseText);
         }
     });
})

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


// Отслеживание нажатия на фильтр "Только неостканированные"
$('#only_not_scan').click(function(){
    onlyNotScanned = this.checked;
    updatePageData();
});


// Отслеживание нажатий на показ отсканированой страницы в компелкте
function view_not_recognized_modal() {
    let scan_id = $(this).attr('id').split('-')[1]
    let file_url = `/api/scanned_page/file/${scan_id}`
    $('.block-page #modal-view-not-recognized iframe').attr('id', `pdf-${scan_id}`).attr('src', file_url)
    $('.block-page').show();
    $('#modal-view-not-recognized').show();
}

// Отслеживание нажатий на показ нераспознанной страницы
function view_recognized_modal() {
    let scan_id = $(this).attr('id').split('-')[1]
    let type = $(this).attr('id').split('-')[0]
    let file_url = ''
    if (type === 'page'){
        file_url = `/api/scanned_page/file/${scan_id}`
    }
    else if (type === 'allpages') {
        file_url = `/api/scanned_page/files/${scan_id}`
    }

    $('.block-page #modal-view-recognized iframe').attr('id', `pdf-${scan_id}`).attr('src', file_url)
    $('.block-page').show();
    $('#modal-view-recognized').show();
}


// Задать номер бланка
$('#modal-view-not-recognized form').submit(function (e) {
    e.preventDefault();
    let number_blank = $(this).serializeArray()[0].value
    let scan_id = $('.block-page #modal-view-not-recognized iframe').attr('id').split('-')[1]

    let data = {
        "event": event_id,
        "organization": organization_id,
        "number_blank": number_blank
    }
    $.ajax({
         type: "PUT",
         url: `${baseURL}/api/scanned_page/${scan_id}`,
         data: JSON.stringify(data),
         dataType: "JSON",
         success: function (jqXHR) {
             console.log("Номер бланка установлен")
             $('.block-page').hide();
             $('#modal-view-not-recognized').hide();
             updatePageData();
         },
         error: function (jqXHR, textStatus, errorThrown) {
             console.log(textStatus, jqXHR.responseText);
         }
    });
})

// Удалить нераспознанную страницу
$('#modal-view-not-recognized .btn-danger').click(function () {
    let scan_id = $('.block-page #modal-view-not-recognized iframe').attr('id').split('-')[1]
    $.ajax({
        type: "DELETE",
        url: `${baseURL}/api/scanned_page/${scan_id}`,
        success: function (response) {
            console.log(`Страница ${scan_id} удалена!`)
            // Перейти на следующую страницу
            console.log(scannedData['error_scanned_page'].length);
            updatePageData().then(r => {
                console.log(scannedData['error_scanned_page'].length);
                if (scannedData['error_scanned_page'].length > 0) {
                    let scan_id = scannedData['error_scanned_page'][0]['id']
                    let file_url = `/api/scanned_page/file/${scan_id}`
                    $('.block-page #modal-view-not-recognized iframe').attr('id', `pdf-${scan_id}`).attr('src', file_url)
                }
                else {
                    $('.block-page #modal-view-not-recognized iframe').attr('id', `pdf-0`).attr('src', '')
                    $('.block-page').hide();
                    $('#modal-view-not-recognized').hide();
                }
            });
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
        }
    });
});


// Закрыть модальное окно отсканированой страницы по кнопке
$('#modal-view-recognized #close-modal').click(function(){
    $('.block-page #modal-view-recognized #pdf').attr('id', `pdf-0`).attr('src', '')
    $('.block-page').hide();
    $('#modal-view-recognized').hide();
});

// Закрыть модальное окно нераспознанной страницы по кнопке
$('#modal-view-not-recognized #close-modal').click(function(){
    $('.block-page #modal-view-not-recognized #pdf').attr('id', `pdf-0`).attr('src', '')
    $('.block-page').hide();
    $('#modal-view-not-recognized').hide();
});


