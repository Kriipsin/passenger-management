from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Schedule, Trip
from .views import generate_dates
from datetime import datetime


@receiver(post_save, sender=Schedule)
def handle_trips_for_schedule(sender, instance, created, **kwargs):
    """
    Automatically handles trips for a schedule when it is created or updated.
    - Creates trips for new schedules.
    - Updates existing trips when a schedule is edited.
    - Removes trips no longer relevant to the updated schedule.
    """
    schedule = instance
    trips_to_create = []
    existing_trip_dates = set()

    # Ensure the start time is properly parsed
    if isinstance(schedule.time, str):
        schedule_time = datetime.strptime(schedule.time, '%Y-%m-%dT%H:%M')  # Handle datetime-local format
    else:
        schedule_time = schedule.time

    # Generate trip dates based on frequency
    if schedule.frequency == "non-regular":
        trip_dates = [schedule_time.date()]  # Single date for non-regular trips
    else:
        trip_dates = generate_dates(schedule_time, schedule.frequency)

    # Process trips for each generated date
    for trip_date in trip_dates:
        # Try to find an existing trip for the same date and schedule
        trip, trip_created = Trip.objects.get_or_create(
            schedule=schedule,
            date=trip_date,  # Use trip_date directly
            defaults={
                "notes": f"Kurs {trip_date}: {schedule.origin}-{schedule.destination}",
            },
        )
        if not trip_created:
            # If the trip already exists, update its notes if necessary
            trip.notes = f"Zaktualizowany kurs {trip_date}: {schedule.origin} to {schedule.destination}"
            trip.save()

        existing_trip_dates.add(trip_date)

    # Remove trips that no longer match the updated schedule
    Trip.objects.filter(schedule=schedule).exclude(date__in=existing_trip_dates).delete()
