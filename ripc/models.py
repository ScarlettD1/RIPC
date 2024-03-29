from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User


class Subject(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name

    @classmethod
    def create(cls, name):
        region = cls(name=name)
        region.save()
        return region


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


class ExpertStatus(models.Model):
    status = models.CharField(max_length=50, default='Работает')


class Expert(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    surname = models.CharField(max_length=30)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    referee = models.BooleanField()
    status = models.ForeignKey(ExpertStatus, on_delete=models.CASCADE)

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


class Admin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    surname = models.CharField(max_length=30)


class RegionRep(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    surname = models.CharField(max_length=30)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)


class OrganizationRep(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    surname = models.CharField(max_length=30)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)


class Event(models.Model):
    name = models.CharField(max_length=300)
    start_date = models.DateField()
    end_date = models.DateField()
    check_times = models.IntegerField()

    def __str__(self):
        return self.name


class Variant(models.Model):
    file_link = models.TextField()
    page_len = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])


class PatternTask(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    max_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])


class Task(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    pattern = models.ForeignKey(PatternTask, on_delete=models.CASCADE)
    answer_coord = ArrayField(ArrayField(models.IntegerField()))
    file_link = models.TextField()


class TaskExpert(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)
    check_date = models.DateTimeField()
    check_time = models.IntegerField()


class Complect(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    file_link = models.TextField()


class Answer(models.Model):
    complect = models.ForeignKey(Complect, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    file_link = models.TextField()
    mark = models.CharField(max_length=10, null=True)


class ThirdMark(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    check_date = models.DateTimeField()
    check_time = models.IntegerField()


class ThirdMarkExpert(models.Model):
    third_mark = models.ForeignKey(ThirdMark, on_delete=models.CASCADE)
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)


class EventStatus(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class OrganizationEvent(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    event_status = models.ForeignKey(EventStatus, on_delete=models.CASCADE)
    percent_status = models.CharField(max_length=3)


class ScannedPage(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    complect = models.ForeignKey(Complect, on_delete=models.CASCADE, null=True)
    file_link = models.TextField()
