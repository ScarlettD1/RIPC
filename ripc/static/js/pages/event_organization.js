let baseURL = `${document.location.protocol}//${document.location.host}`
let usageOrganization = []
let organizations = {}
let event_id = 0
let page = 1
let lastPage = 1
let sortBy = 'organization'

$(document).ready(function(){
    getStartData();
    getPageInfo();
    setInterval(getPageInfo, 30000);
    $('.organizations-event-table button').bind('click', SortData)
});

// Получить стартовые данные
function getStartData() {
    event_id = Number(window.location.pathname.split('/')[2])
}

function getPageInfo() {
    // Информация о МП
     $.ajax({
        type: "GET",
        url: `${baseURL}/api/event/?id=${event_id}`,
        dataType: 'JSON',
        success: function (response) {
            console.log("Информация о МП получена!")
            $('header .event-name').html(response['name'])
            $('header .event-datas').html(`${response['start_date']} - ${response['end_date']}`)
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
        }
    });

    // Информация о организациях в МП!
     $.ajax({
        type: "GET",
        url: `${baseURL}/api/event_organization/?event=${event_id}&page=${page}&order_by=${sortBy}`,
        dataType: 'JSON',
        success: function (response) {
            console.log("Информация о организациях в МП получена!")

            // Заполнение полученными данными
            let table_rows = ``
            let org_events = response['event_organizations']
            for (let i=0; i<org_events.length; i++){
                let eventOrganization = org_events[i]
                usageOrganization.push(Number(eventOrganization['organization']['id']));

                // Поиск цвета процентов статуса
                let percent_status_color = ''
                if (eventOrganization['percent_status'] <= 25) percent_status_color = '#ff2c40'
                else if (eventOrganization['percent_status'] <= 50) percent_status_color = '#ffaa00'
                else if (eventOrganization['percent_status'] <= 75) percent_status_color = '#ffd700'
                else if (eventOrganization['percent_status'] <= 100) percent_status_color = '#b7ff00'

                table_rows += `
                    <tr id=${ eventOrganization['id'] }>
                        <td class="table-checkbox"><input class="checkbox w-100" type="checkbox"></td>
                        <td class="organization text-start w-50">
                            <a class="link-primary fw-bold" href="/event/${ event_id }/?organization_id=${ eventOrganization['organization']['id'] }">${ eventOrganization['organization']['name'] }</a>
                        </td>
                        <td class="number_participants">${ eventOrganization['number_participants'] }</td>
                        <td class="event_status">
                            <div class="table-filed-color" style="background-color: ${ eventOrganization['event_status']['color_hex'] }">
                                ${ eventOrganization['event_status']['name'] }
                            </div>
                        </td>
                        <td class="percent_status">
                            <div class="table-filed-color" style="background-color: ${ percent_status_color }">
                                ${eventOrganization['percent_status']}%
                            </div>
                        </td>
                    </tr>
                 `
            }
            $('.page-block .organizations #organizations-event .table tbody').html(table_rows)

            lastPage = response['total_page']
            insertPagination(lastPage)

        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
        }
    });
}

function SortData() {
    if ($(this).attr('id').split('-')[1] === sortBy)
        sortBy = '-' + sortBy
    else
        sortBy = $(this).attr('id').split('-')[1]
    getPageInfo()
}

// Открыть окно добавление организации
$('.page-block .organizations .organizations-event-form .btn-toolbar .btn-primary').click(function(){
    $.ajax({
        type: "GET",
        url: `${baseURL}/api/organization/`,
        dataType: 'JSON',
        success: function (response) {
            console.log("Организации получены!")
            // Заполнение полученными данными
            let inputOrganization = `<option disabled>Организация</option>`
            for (let i=0; i<response.length; i++){
                organizations[response[i].id] = response[i].name
                if (!(usageOrganization.includes(response[i].id))) {
                    inputOrganization += `<option value=${response[i].id}>${response[i].name}</option>`
                }
            }
            $('.modal-add-organization form #inputOrganization').html(inputOrganization)
            $('.block-page').show();
            $('.modal-add-organization').show();
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
        }
    });
});

// Добавить организацию
$("#modal-add-organization form").submit(function (e) {
    e.preventDefault();
    let org_id = $(this).serializeArray()[0].value
    let data = {
        "event": event_id,
        "event_status": '1',
        "organization": org_id,
        "percent_status": '100',
        "number_participants": '0'
    }
     $.ajax({
         type: "POST",
         url: `${baseURL}/api/event_organization/`,
         data: JSON.stringify(data),
         dataType: "JSON",
         success: function (jqXHR) {
             console.log("Организация добавлена")
             usageOrganization.push(Number(org_id));
             getPageInfo();
             $('.block-page').hide();
             $('.modal-add-organization').hide();
             $(`.page-block .matching-templates .btn-primary`).prop("selectedIndex", 1);
         },
         error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
         }
     });
});

// Закрыть окно добавление организации
$('#modal-add-organization #close-modal').click(function(){
    $('.block-page').hide();
    $('.modal-add-organization').hide();
});


// Удаление выделенных полей
$('.page-block .organizations .organizations-event-form .btn-toolbar .btn-danger').click(function(){
    let table_rows = $(this).parent().parent().find('.table').find('tbody')
    let rows = table_rows.children('tr')

    let ids = []

    $(rows).each(function (){
        if ($(this).find('.checkbox').is(':checked')){
            ids.push($(this).attr('id'))
        }
    });
    if (ids.length === 0) {
        return
    }

    $.ajax({
        type: "DELETE",
        url: `${baseURL}/api/event_organization/?id=${ids}`,
        success: function (jqXHR) {
            console.log("Организации удалены из мероприятия")
            getPageInfo();
            for (let i in ids) {
                usageOrganization.splice(usageOrganization.indexOf(ids[i]), 1);
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
        }
    });
});


function insertPagination(lastPage) {
    let pagination = `
        <li class="page-item">
            <button class="page-link page-btn-first" aria-label="Previous">
                <span aria-hidden="true">&laquo;</span>
            </button>
        </li>
    `

    let pagesRight = page + 2
    let pagesLeft = page - 3

    if (pagesLeft < 0) {
        pagesRight -= pagesLeft
        pagesLeft -= pagesLeft
    }

    if (pagesRight > lastPage) {
        pagesLeft -= pagesRight - lastPage
        pagesRight = lastPage
    }

    if (pagesLeft < 0) {
        pagesLeft = 0
    }

    for (let i=pagesLeft; i<pagesRight; i++) {
        pagination += `<li class="page-item page-num-nav"><button class="page-link page-btn" id="page-${i+1}">${i+1}</button></li>`
    }

    pagination += `
        <li class="page-item">
            <button class="page-link page-btn-last" aria-label="Next">
                <span aria-hidden="true">&raquo;</span>
            </button>
        </li>
    `
    $('.pagination').html(pagination)
    $('.pagination li .page-btn-first').bind('click', choice_first_page)
    $('.pagination li .page-btn').bind('click', choice_page);
    $('.pagination li .page-btn-last').bind('click', choice_last_page);
}


// Переход на другую страницу таблицы
function choice_page() {
    page = Number($(this).attr('id').split('-')[1])
    getPageInfo()
}

// Переход на первую страницу таблицы
function choice_first_page () {
    page = 1
    getPageInfo()
}

// Переход на последнюю страницу таблицы
function choice_last_page (){
    page = lastPage
    getPageInfo()
}