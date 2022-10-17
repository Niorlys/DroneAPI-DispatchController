from rest_framework import serializers
from .models import *
import re


class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = '__all__'


    def validate_name(self, value):
        if re.search("[^a-zA-Z0-9_-]", value):
            raise serializers.ValidationError('Name must contain only letters, numbers or -, _ characters')
        return value

    def validate_code(self, value):
        if re.search("[^A-Z0-9_]", value):
            raise serializers.ValidationError('Code must contain only uppercase letters, numbers or  _ characters')
        return value


# This is for serializing medications to be show
# in the list of loaded medication of a drone
class DroneMedicationM2MSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = ['name', 'weight', 'code', 'picture']


# This is for displaying drone information on GET
class DroneReadSerializer(serializers.ModelSerializer):
    medications = DroneMedicationM2MSerializer(many=True)

    class Meta:
        model = Drone
        fields = '__all__'


class DroneCreateSerializer(serializers.ModelSerializer):
    weight_limit = serializers.IntegerField(min_value=100, max_value=500)
    #medications = serializers.PrimaryKeyRelatedField(many=True, queryset=Medication.objects.all())
    battery = serializers.IntegerField(default=100, read_only=True)
    load = serializers.IntegerField(read_only=True)
    state = serializers.CharField(read_only=True)

    class Meta:
        model = Drone
        fields = '__all__'

    def validate_serial(self, value):
        if not value.isnumeric():
            raise serializers.ValidationError('Serial must contain only numbers')
        return value

    def validate_state(self, value):
        choices = ('Idle','Loading','Loaded','Delivering','Delivered','Returning')
        if not value in choices:
            print('VALUE STATE', value)
            raise serializers.ValidationError(f'Invalid choice, select among {choices}')
        return value

    def validate_model(self, value):
        choices = ('Lightweight', 'Middleweight', 'Cruiserweight', 'Heavyweight')
        if not value in choices:
            raise serializers.ValidationError(f'Invalid choice, select among {choices}')
        return value


class DroneUpdateSerializer(serializers.Serializer):
    medications = serializers.PrimaryKeyRelatedField(many=True, queryset=Medication.objects.all())
    battery = serializers.IntegerField(min_value=0, max_value=100)
    state = serializers.CharField()

    class Meta:
        model = Drone
        fields = ['medications', 'battery', 'state']


    def validate_state(self, value):
        choices = ('Idle', 'Loading', 'Loaded', 'Delivering', 'Delivered', 'Returning')
        if not value in choices:
            print('VALUE STATE', value)
            raise serializers.ValidationError(f'Invalid choice, select among {choices}')
        return value

    def validate_model(self, value):
        choices = ('Lightweight', 'Middleweight', 'Cruiserweight', 'Heavyweight')
        if not value in choices:
            raise serializers.ValidationError(f'Invalid choice, select among {choices}')
        return value

    def update(self, instance, validated_data):

        medications = validated_data.pop('medications') if 'medications' in validated_data else None
        for medication in medications:
            instance.load += medication.weight
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if medications:
            instance.medications.set(medications)
        instance.save()
        return instance
