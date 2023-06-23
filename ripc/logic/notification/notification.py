from ripc.models import Notification, EventExperts
from datetime import datetime


# Функция добавляющая уведомления для администраторов
def notify(expert_id, org_event_id, not_type):
    event_expert = EventExperts.objects.filter(event=org_event_id, expert_id=expert_id)
    message = ''
    match not_type:
        case 'fast':
            message = 'Обнаружена слишком быстрая проверка'
        case 'slow':
            message = 'Обнаружено, что эксперт сильно отстает от плановых показателей'
    Notification.create(datetime.date(datetime.now()), event_expert, message)
