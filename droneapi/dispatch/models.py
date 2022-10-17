from django.db import models
def user_directory_path(instance, filename):
    # image file will be uploaded to MEDIA_ROOT/<Medication_id_filename>
    return f'Medication_{instance.name}_{filename}'


# Medication template
class Medication(models.Model):
    name = models.CharField(max_length=200)
    weight = models.IntegerField()
    code = models.CharField(max_length=200, unique=True)
    picture = models.ImageField(upload_to=user_directory_path, height_field=None, width_field=None
                                , max_length=None, default="default.jpg", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# Many to many auxiliary table
class MedicationMembership(models.Model):
    drone = models.ForeignKey("Drone", on_delete=models.CASCADE)
    medication = models.ForeignKey('Medication', on_delete=models.CASCADE)


# Drone template
class Drone(models.Model):
    serial = models.CharField(max_length=100, unique=True, blank = True)
    model = models.CharField(max_length=15, default='Heavyweight',blank=True)
    weight_limit = models.IntegerField(default=500)
    battery = models.IntegerField(default=100, blank=True)
    state = models.CharField(max_length=10, default='Idle',blank=True)
    medications = models.ManyToManyField(Medication, related_name='medications', through=MedicationMembership)
    load = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Drone: {self.serial}'
