from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User


# Файл с моделями - таблицами в базе данных
# Модель предметных областей
class Subject(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


# Модель региона
class Region(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name

    @classmethod
    def create(cls, name):
        region = cls(name=name)
        region.save()
        return region


# Модель организации
class Organization(models.Model):
    name = models.CharField(max_length=300)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @classmethod
    def create(cls, name, region):
        org = cls(name=name, region=region)
        org.save()
        return org


# Модель статусов экспертов
class ExpertStatus(models.Model):
    status = models.CharField(max_length=50, default='Работает')


# Модель эксперта
class Expert(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    surname = models.CharField(max_length=30)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    referee = models.BooleanField()
    status = models.ForeignKey(ExpertStatus, on_delete=models.CASCADE)
    delta = models.IntegerField()

    @classmethod
    def create(cls, data):
        user = User.objects.create_user(data['username'], data['email'], data['password'])
        user.last_name = data['last_name']
        user.first_name = data['first_name']
        user.save()

        org = Organization.objects.get(pk=data['organization'])
        subject = Subject.objects.get(pk=data['subject'])

        expert = cls(surname=data['surname'], user=user, referee=data['referee'], org=org, subject=subject)
        expert.save()
        return expert


# Модель администратора
class Admin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    surname = models.CharField(max_length=30)


# Модель представителя региона
class RegionRep(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    surname = models.CharField(max_length=30)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)


# Модель представителя организации
class OrganizationRep(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    surname = models.CharField(max_length=30)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)


# Модель мероприятия
class Event(models.Model):
    name = models.CharField(max_length=300)
    start_date = models.DateField()
    end_date = models.DateField()
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# Модель варианта
class Variant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    page_count = models.CharField(max_length=2)
    file_path = models.TextField(null=True)


# Модель вырезки варианта
class VariantCropping(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    task_num = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    answer_coord = ArrayField(models.IntegerField())


# Модель шаблона задания
class PatternTask(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    task_num = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    max_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    check_times = models.IntegerField()


# Модель критерий
class Criteria(models.Model):
    variant = models.OneToOneField(Variant, on_delete=models.CASCADE)
    file_path = models.TextField(null=True)


# Модель вырезки критериев
class CriteriaCropping(models.Model):
    criteria = models.ForeignKey(Criteria, on_delete=models.CASCADE)
    task_num = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    file_path = models.TextField(null=True)


# Модель задания
class Task(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    pattern = models.ForeignKey(PatternTask, on_delete=models.CASCADE)
    variant_cropping = models.ForeignKey(VariantCropping, on_delete=models.CASCADE)
    criteria_cropping = models.ForeignKey(CriteriaCropping, on_delete=models.CASCADE)
    task_num = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])


# Смежная модель задания-эксперта
class TaskExpert(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)
    check_date = models.DateTimeField()
    check_time = models.IntegerField()


# Модель статуса мероприятия
class EventStatus(models.Model):
    name = models.CharField(max_length=20)
    color_hex = models.CharField(validators=[MinLengthValidator(6)], max_length=7)


# Расширенная модель мероприятия на организацию
class OrganizationEvent(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    event_status = models.ForeignKey(EventStatus, on_delete=models.CASCADE)
    percent_status = models.TextField(max_length=4, null=True)
    number_participants = models.TextField(max_length=5, null=True)


# Смежная модель мероприятия-эксперта
class EventExperts(models.Model):
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)
    event = models.ForeignKey(OrganizationEvent, on_delete=models.CASCADE)


# Модель комплекта
class Complect(models.Model):
    organization_event = models.ForeignKey(OrganizationEvent, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    is_additional = models.BooleanField(default=False)
    file_path = models.TextField(null=True)


# Модель ответа студента
class Answer(models.Model):
    complect = models.ForeignKey(Complect, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    file_path = models.TextField(null=True)
    mark = models.CharField(max_length=10, null=True)


# Модель 3 оценки ответа
class ThirdMark(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    check_date = models.DateTimeField()
    check_time = models.IntegerField()


# Смежная таблица 3 оценки-эксперта
class ThirdMarkExpert(models.Model):
    third_mark = models.ForeignKey(ThirdMark, on_delete=models.CASCADE)
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)


# Модель отсканированных страниц
class ScannedPage(models.Model):
    organization_event = models.ForeignKey(OrganizationEvent, on_delete=models.CASCADE)
    complect = models.ForeignKey(Complect, on_delete=models.CASCADE, null=True)
    page_number = models.CharField(max_length=2, null=True)
    file_path = models.TextField(null=True)


# Модель уведомления
class Notification(models.Model):
    date = models.DateField()
    event_expert = models.ForeignKey(EventExperts, on_delete=models.CASCADE)
    message = models.CharField(max_length=300)

    @classmethod
    def create(cls, date, event_expert, message):
        notification = cls(date=date, event_expert=event_expert, message=message)
        notification.save()
        return notification
