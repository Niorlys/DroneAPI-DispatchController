from .models import *
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .serializers import DroneCreateSerializer, DroneReadSerializer, MedicationSerializer
from .serializers import DroneMedicationM2MSerializer
from .serializers import DroneUpdateSerializer
from django.db.models import F
from rest_framework.decorators import action

class DroneView(viewsets.ModelViewSet):
    queryset = Drone.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return DroneUpdateSerializer
        if self.request.method == 'POST':
            return DroneCreateSerializer
        return DroneReadSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get('state', None) == 'Loading' and \
                serializer.validated_data.get('battery', instance.battery) < 25:
            return Response(f"Unable to load since battery is too low: {instance.battery}%", status.HTTP_400_BAD_REQUEST)
        total_medication_weight = 0
        for medication in serializer.validated_data['medications']:
            total_medication_weight += medication.weight
        if total_medication_weight > instance.weight_limit:
            return Response("Medication's weight exceed drone's limit", status.HTTP_400_BAD_REQUEST)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(methods=['get'], detail=True, url_path='medication')
    def check_loaded_medication(self, request, pk=None):
        try:
            drone = Drone.objects.get(id=pk)
        except Drone.DoesNotExist:
            return Response(f'Bad request, there not exists drone with id {pk}', status.HTTP_400_BAD_REQUEST)
        queryset = self.filter_queryset(drone.medications.all())

        page = self.paginate_queryset(queryset)
        if page is not None:
            kwargs = {'many': True}
            kwargs.setdefault('context', self.get_serializer_context())
            serializer = DroneMedicationM2MSerializer(page, **kwargs)
            return self.get_paginated_response(serializer.data)

        serializer = DroneMedicationM2MSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False, url_path='available')
    def check_available_drones(self, request):
        # A drone is available for loading if it is in idle state, it has not reached the weight limit
        # and its battery level is above 25%
        queryset = Drone.objects.filter(state='Idle', load__lt=F('weight_limit'), battery__gt=25)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, url_path='battery')
    def check_drone_battery(self, request, pk = None):
        try:
            instance = Drone.objects.get(id=pk)
        except Drone.DoesNotExist:
            return Response(f'Bad request, there not exists drone with id {pk}', status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance)
        return Response({'battery': serializer.data['battery']})


class MedicationView(viewsets.ModelViewSet):
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer

