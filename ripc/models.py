import uuid

from django.conf import settings
from django.db import models


class Subject(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Organization(models.Model):
    name = models.CharField(max_length=300)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Expert(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    mail = models.CharField(max_length=50)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    referee = models.BooleanField()


class Admin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class RegionRep(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)


class OrganizationRep(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)


class Event(models.Model):
    name = models.CharField(max_length=300)
    start_date = models.DateField()
    end_date = models.DateField()
    check_times = models.IntegerField()

    def __str__(self):
        return self.name


class Task(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    task = models.UUIDField(default=uuid.uuid4())


class TaskExpert(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)
    check_date = models.DateTimeField()
    check_time = models.IntegerField()


class Answer(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    mark = models.CharField(max_length=10)
    answer = models.UUIDField(default=uuid.uuid4())


class ThirdMark(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    check_date = models.DateTimeField()
    check_time = models.IntegerField()


class ThirdMarkExpert(models.Model):
    third_mark = models.ForeignKey(ThirdMark, on_delete=models.CASCADE)
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)
