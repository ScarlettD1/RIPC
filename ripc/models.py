from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.db import models
from django.contrib.postgres.fields import ArrayField


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

    def __str__(self):
        return self.name


class Variant(models.Model):
    page_count = models.CharField(max_length=2)
    file_path = models.TextField(null=True)


class VariantCropping(models.Model):
    answer_coord = ArrayField(models.IntegerField())
    task_file_path = models.TextField(null=True)


class PatternTask(models.Model):
    name = models.CharField(max_length=300)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    max_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    check_times = models.IntegerField()


class Task(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    pattern = models.ForeignKey(PatternTask, on_delete=models.CASCADE)
    cropping = models.ForeignKey(VariantCropping, on_delete=models.CASCADE)


class TaskExpert(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)
    check_date = models.DateTimeField()
    check_time = models.IntegerField()


class Complect(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    is_additional = models.BooleanField(default=False)
    file_path = models.TextField(null=True)


class Answer(models.Model):
    complect = models.ForeignKey(Complect, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    file_path = models.TextField(null=True)
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
    color_hex = models.CharField(validators=[MinLengthValidator(6)], max_length=7)


class OrganizationEvent(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    event_status = models.ForeignKey(EventStatus, on_delete=models.CASCADE)
    percent_status = models.TextField(max_length=3, null=True)
    number_participants = models.TextField(max_length=5, null=True)


class ScannedPage(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    complect = models.ForeignKey(Complect, on_delete=models.CASCADE, null=True)
    page_number = models.CharField(max_length=2, null=True)
    file_path = models.TextField(null=True)
