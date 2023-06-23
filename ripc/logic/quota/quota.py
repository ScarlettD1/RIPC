from ...models import *


# Класс расчета плановых показателей:
class Quota:
    # прогноз даты завершения проверки и квота проверки по каждому предмету, каждого эксперта
    def __init__(self, experts, event_id, multiplicity, count):
        org_event = OrganizationEvent.objects.get(event=event_id)
        task_set = Complect.objects.get(organization_event=org_event.id)
        tasks = Task.objects.filter(task_set.id)

        temp = {}
        quota = []
        subject_time = []

        for task in tasks:
            temp[task.subject] += task.norm_time * count[task.id]
        for subject in range(len(temp)):
            ex_count = len(experts[subject])
            quota_time = multiplicity * temp / ex_count * pow(1.05, multiplicity - 1)
            self.quota = quota_time
            self.quota_expert = quota_time / 8
            quota.append(quota_time)
            subject_time.append(max(quota))
        self.end_culc = max(subject_time)
