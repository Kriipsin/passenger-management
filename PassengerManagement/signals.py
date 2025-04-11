from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Schedule, Trip, Reservation
from .views import generate_dates
from datetime import datetime
from .views import update_trip_statuses

@receiver(post_save, sender=Schedule)
def handle_trips_for_schedule(sender, instance, created, **kwargs):

    schedule = instance
    existing_trip_dates = set()

    if isinstance(schedule.time, str):
        schedule_time = datetime.strptime(schedule.time, '%Y-%m-%dT%H:%M')
    else:
        schedule_time = schedule.time

    if schedule.frequency == "non-regular":
        trip_dates = [schedule_time.date()]
    else:
        trip_dates = generate_dates(schedule_time, schedule.frequency)

    for trip_date in trip_dates:
        trip, trip_created = Trip.objects.get_or_create(
            schedule=schedule,
            date=trip_date,
            defaults={
                "notes": f"Kurs {trip_date}: {schedule.origin}-{schedule.destination}",
            },
        )
        if not trip_created:
            trip.notes = f"Zaktualizowany kurs {trip_date}: {schedule.origin} to {schedule.destination}"
            trip.save()

        existing_trip_dates.add(trip_date)

    Trip.objects.filter(schedule=schedule).exclude(date__in=existing_trip_dates).delete()


@receiver(post_save, sender=Schedule)
def schedule_saved(sender, instance, **kwargs):
    update_trip_statuses()


@receiver(post_save, sender=Trip)
def trip_saved(sender, instance, **kwargs):
    update_trip_statuses()


@receiver(post_save, sender=Reservation)
def reservation_saved(sender, instance, **kwargs):
    update_trip_statuses()