from django.db import models

# Create your models here.
class Passenger(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.first_name + " " + self.last_name

class Vehicle(models.Model):
    license_plate = models.CharField(max_length=10)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    seats = models.IntegerField()
    review_date = models.DateField(blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.make + " " + self.model + " (" + self.license_plate + ")"

class Driver(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    active = models.BooleanField(default=True)
    license_number = models.CharField(max_length=15, blank=True)
    license_expiry = models.DateField(blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.first_name + " " + self.last_name

class Schedule(models.Model):
    time = models.DateTimeField()
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    frequency = models.CharField(max_length=50, choices=[("daily", "Daily"), ("weekly", "Weekly"), ("monthly", "Monthly"), ("not-regular", "Not regular")], default="daily")

    def __str__(self):
        return self.origin + " - " + self.destination

class Trip(models.Model):
    date = models.DateField()
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    vehicle = models.ForeignKey('Vehicle', on_delete=models.SET_NULL, null=True, blank=True)
    driver = models.ForeignKey('Driver', on_delete=models.SET_NULL, null=True, blank=True)
    passengers = models.ManyToManyField('Passenger')
    status = models.CharField(
        max_length=50,
        choices=[
            ('planned', 'Planned'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='planned',
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Trip from {self.schedule.origin} to {self.schedule.destination}"
