from django.contrib import admin
from .models import Passenger, Vehicle, Driver, Schedule, Trip

# Register your models here.
admin.site.register(Passenger)
admin.site.register(Vehicle)
admin.site.register(Driver)
admin.site.register(Schedule)
admin.site.register(Trip)

