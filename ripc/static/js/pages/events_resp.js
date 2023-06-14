let baseURL = `${document.location.protocol}//${document.location.host}`
let page = 1
let lastPage = 1
let sortBy = 'start_date'

$(document).ready(function(){
    getEventsInfo();
    setInterval(getEventsInfo, 30000);
    $('.table-admin-view thead button').bind('click', SortData)
});

// Получить стартовые данные
function getEventsInfo() {
    $.ajax({
        type: "GET",
        url: `${baseURL}/api/event/?page=${page}&order_by=${sortBy}`,
        dataType: 'JSON',
        success: function (response) {
            console.log("Мероприятия получены!")

            // Заполнение полученными данными
            let events = response['events']
            let eventsTable = ``
            for (let i=0; i<events.length; i++){
                let percent_status_color = ''
                if (events[i]['total_percent'] <= 25) percent_status_color = '#ff2c40'
                else if (events[i]['total_percent'] <= 50) percent_status_color = '#ffaa00'
                else if (events[i]['total_percent'] <= 75) percent_status_color = '#ffd700'
                else if (events[i]['total_percent'] <= 100) percent_status_color = '#b7ff00'

                let aLinkStyle = "link-primary"
                if (events[i]['not_create']) {
                    aLinkStyle = "link-danger"
                }

                eventsTable += `
                    <tr id="${events[i]['id']}">
                        <td class="table-checkbox"><input class="checkbox w-100" type="checkbox"></td>
                        <th style="width: auto"><a href="/event_organization/${events[i]['id']}" class=${aLinkStyle}>${events[i]['name']}</a></th>
                        <td>${events[i]['start_date']}</td>
                        <td>${events[i]['end_date']}</td>
                        <td>${events[i]['orgs_count']}</td>
                        <td>
                            <div class="table-filed-color" style="background-color: ${ percent_status_color }"> ${events[i]['total_percent']}%</div>
                        </td>
                    </tr>
                `
            }
            $('.table-admin-view tbody').html(eventsTable)

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
    getEventsInfo()
}

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

// Создание МП
$('.page-block .btn-toolbar .btn-primary').click(function(){
    window.location.href = `${baseURL}/create_event`;
})


// Удаление выделенных МП
$('.page-block .btn-toolbar .btn-danger').click(function(){
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
        url: `${baseURL}/api/event/?id=${ids}`,
        success: function (jqXHR) {
            console.log("Мероприятия удалены!")
            getEventsInfo()
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
        }
    });
})

// Переход на другую страницу таблицы
function choice_page() {
    page = Number($(this).attr('id').split('-')[1])
    getEventsInfo()
}

// Переход на первую страницу таблицы
function choice_first_page () {
    page = 1
    getEventsInfo()
}

// Переход на последнюю страницу таблицы
function choice_last_page (){
    page = lastPage
    getEventsInfo()
}