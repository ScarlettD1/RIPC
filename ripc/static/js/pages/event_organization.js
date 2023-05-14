let baseURL = "http://127.0.0.1:8000"
let usageOrganization = []
let organizations = {}
let event_id = 0
$(document).ready(function(){
    getStartData();
});

// Получить стартовые данные
function getStartData() {
    $('#startData #organization').children().each(function(i,elem) {
        usageOrganization.push(Number(elem.innerText))
    })
    event_id = Number($('#startData #event_id')[0].innerText)
    $('#startData').remove();
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
            for (let i=0; i<response.length; i++){
                organizations[response[i].id] = response[i].name
                if (!(usageOrganization.includes(response[i].id))) {
                    $('.modal-add-organization form #inputOrganization').append(`<option value=${response[i].id}>${response[i].name}</option>`)
                }
            }
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
    let table_rows = $('.page-block .organizations #organizations-event .table tbody')

    let org_id = $(this).serializeArray()[0].value
    let data = {
        "event": $(this).attr('id'),
        "event_status": '1',
        "organization": org_id,
        "percent_status": '100',
        "number_participants": '0'
    }
     $.ajax({
         type: "POST",
         url: `${baseURL}/api/event_organization/?get_full=True`,
         data: JSON.stringify(data),
         dataType: "JSON",
         success: function (jqXHR) {
             console.log("Организация добавлена")
             usageOrganization.push(Number(org_id));
             let eventOrganization = jqXHR[0][0]
             let percent_status_color = ''
             if (eventOrganization['percent_status'] <= 25) percent_status_color = '#ff0000'
             else if (eventOrganization['percent_status'] <= 50) percent_status_color = '#ffaa00'
             else if (eventOrganization['percent_status'] <= 75) percent_status_color = '#ffd700'
             else if (eventOrganization['percent_status'] <= 100) percent_status_color = '#b7ff00'

             table_rows.append(`
                <tr id=${ eventOrganization.id }>
                    <td class="table-checkbox"><input class="checkbox w-100" type="checkbox"></td>
                    <td class="organization w-50">
                        <a href="/event/${ event_id }/?organization_id=${ eventOrganization['organization']['id'] }">${ eventOrganization['organization']['name'] }</a>
                    </td>
                    <td class="number_participants">${ eventOrganization['number_participants'] }</td>
                    <td class="event_status">
                        <div class="table-filed-color" style="background-color: ${ eventOrganization['event_status']['color_hex'] }">
                            ${ eventOrganization['event_status']['name'] }
                        </div>
                    </td>
                    <td class="percent_status">
                        <div class="table-filed-color" style="background-color: ${ percent_status_color }">
                            ${ eventOrganization['percent_status'] }%
                        </div>
                    </td>
                </tr>
             `);
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
    let del_rows = []

    $(rows).each(function (){
        if ($(this).find('.checkbox').is(':checked')){
            ids.push($(this).attr('id'))
            del_rows.push($(this));
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
            $.each(del_rows, function (index, value) {
                value.remove();
            });
            for (let i in ids) {
                usageOrganization.splice(usageOrganization.indexOf(ids[i]), 1);
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, jqXHR.responseText);
        }
    });
});