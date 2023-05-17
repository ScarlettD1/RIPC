from django.template.defaulttags import register
from rest_framework import serializers
from .models import Subject, Event, Variant, PatternTask, VariantCropping, Task, OrganizationEvent, Organization, \
    Region, EventStatus, ScannedPage, Complect


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name', 'start_date', 'end_date']


class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ['id', 'page_count', 'file_path']


class VariantCroppingSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantCropping
        fields = ['id', 'answer_coord', 'task_file_path']


class PatternTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatternTask
        fields = ['id', 'name', 'max_score', 'subject', 'check_times']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'variant', 'pattern', 'cropping']


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['name']


class OrganizationSerializer(serializers.ModelSerializer):
    region = RegionSerializer(read_only=True)

    class Meta:
        model = Organization
        fields = ['id', 'name', 'region']


class EventStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventStatus
        fields = ['name', 'color_hex']


class OrganizationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationEvent
        fields = ['id', 'event', 'event_status', 'organization', 'percent_status', 'number_participants']


class ComplectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complect
        fields = ['id', 'organization', 'event', 'variant', 'is_additional', 'file_path']


class ScannedPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScannedPage
        fields = ['id', 'organization', 'complect', 'page_number', 'file_path']


@register.filter()
def to_int(value):
    return int(value)
