from django.conf import settings
from django.db import models


class Subject(models.Model):
    sub_name = models.CharField(max_length=200)

    def __str__(self):
        return self.sub_name


class Expert(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    # name = models.CharField(max_length=30)
    # second_name = models.CharField(max_length=30)
    # surname = models.CharField(max_length=30)
    mail = models.CharField(max_length=50)

    # def __str__(self):
    #     return self.second_name + self.second_name + self.surname


class Admin(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # name = models.CharField(max_length=30)
    # second_name = models.CharField(max_length=30)
    # surname = models.CharField(max_length=30)

    # def __str__(self):
    #     return .second_name + self.second_name + self.surname


class Event(models.Model):
    name = models.CharField(max_length=300)
    date_begin = models.DateField
    deadline = models.DateField

    # subjects - id's предметов, названия хранить отдельно
    def __str__(self):
        return self.date_begin


class Organization(models.Model):
    org_name = models.CharField(max_length=300)

    # experts
    # city
    def __str__(self):
        return self.org_name
