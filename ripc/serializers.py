from rest_framework import serializers
from .models import Subject, Event, Variant, PatternTask


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name', 'start_date', 'end_date', 'check_times']


class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ['id', 'file_path']


class PatternTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatternTask
        fields = ['id', 'name', 'max_score', 'subject']
