from .views import DroneView, MedicationView
from django.urls import path
from rest_framework.routers import SimpleRouter

# ViewSets routers
router = SimpleRouter()
router.register('', DroneView, basename='Drones')
router.register('drone/medications', MedicationView, basename='Medication')

urlpatterns = router.urls