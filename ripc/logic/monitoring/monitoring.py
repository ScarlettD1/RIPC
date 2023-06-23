from ripc.logic.notification.notification import notify
from ripc.models import OrganizationEvent, TaskExpert


# Функция мониторинга, вызываемая на проверку успеваемости экспертов на мероприятии
def monitoring(org_event_id, quota):
    tasks = TaskExpert.objects.filter(event=org_event_id)
    experts = {}
    for task in tasks:
        experts[task.expert] = task.expert.delta
    for expert in experts:
        if expert.delta > 2 * quota.quota_expert[expert.subject]:
            notify(expert.id, org_event_id, 'slow')
        elif expert.delta < 2 * quota.quota_expert[expert.subject]:
            notify(expert.id, org_event_id, 'fast')
