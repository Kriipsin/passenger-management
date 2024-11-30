from django.shortcuts import render, redirect, get_object_or_404
from .models import Passenger, Vehicle, Driver, Schedule, Trip, Reservation
from datetime import timedelta, datetime
from django.utils.timezone import now, make_aware
from django.http import JsonResponse
from django.db.models import Sum, F, Q


# Create your views here.
def home(request):
    return render(request, 'home.html')
def passenger_list(request):
    passengers = Passenger.objects.all()
    return render(request, 'passenger_management/passenger_list.html', {'passengers': passengers})


def passenger_add(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')

        Passenger.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number
        )

        return redirect('passenger_list')
    return render(request, 'passenger_management/passenger_add.html')


def passenger_edit(request, passenger_id):
    passenger = get_object_or_404(Passenger, id=passenger_id)

    if request.method == 'POST':
        passenger.first_name = request.POST.get('first_name')
        passenger.last_name = request.POST.get('last_name')
        passenger.email = request.POST.get('email')
        passenger.phone_number = request.POST.get('phone_number')
        passenger.save()

        return redirect('passenger_list')

    return render(request, 'passenger_management/passenger_edit.html', {'passenger': passenger})

def passenger_delete(request, passenger_id):
    passenger = get_object_or_404(Passenger, id=passenger_id)
    passenger.delete()
    return redirect('passenger_list')


def vehicle_list(request):
    vehicles = Vehicle.objects.all()
    return render(request, 'vehicle_management/vehicle_list.html', {'vehicles': vehicles})

def vehicle_add(request):
    if request.method == 'POST':
        license_plate = request.POST.get('license_plate')
        make = request.POST.get('make')
        model = request.POST.get('model')
        year = request.POST.get('year')
        seats = request.POST.get('seats')
        review_date = request.POST.get('review_date')
        notes = request.POST.get('notes')

        Vehicle.objects.create(
            license_plate=license_plate,
            make=make,
            model=model,
            year=year,
            seats=seats,
            review_date=review_date,
            notes=notes
        )

        return redirect('vehicle_list')
    return render(request, 'vehicle_management/vehicle_add.html')

def vehicle_edit(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    if request.method == 'POST':
        vehicle.license_plate = request.POST.get('license_plate')
        vehicle.make = request.POST.get('make')
        vehicle.model = request.POST.get('model')
        vehicle.year = request.POST.get('year')
        vehicle.seats = request.POST.get('seats')
        vehicle.review_date = request.POST.get('review_date')
        vehicle.notes = request.POST.get('notes')
        vehicle.save()

        return redirect('vehicle_list')

    return render(request, 'vehicle_management/vehicle_edit.html', {'vehicle': vehicle})

def vehicle_delete(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    vehicle.delete()
    return redirect('vehicle_list')

def driver_list(request):
    drivers = Driver.objects.all()
    return render(request, 'driver_management/driver_list.html', {'drivers': drivers})

def driver_add(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        active = 'active' in request.POST
        license_number = request.POST.get('license_number')
        license_expiry = request.POST.get('license_expiry')
        notes = request.POST.get('notes')

        Driver.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            active=active,
            license_number=license_number,
            license_expiry=license_expiry,
            notes=notes
        )

        return redirect('driver_list')
    return render(request, 'driver_management/driver_add.html')


def driver_edit(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)

    if request.method == 'POST':
        driver.first_name = request.POST.get('first_name')
        driver.last_name = request.POST.get('last_name')
        driver.phone_number = request.POST.get('phone_number')
        driver.email = request.POST.get('email')
        driver.active = 'active' in request.POST
        driver.license_number = request.POST.get('license_number')
        driver.license_expiry = request.POST.get('license_expiry')
        driver.notes = request.POST.get('notes')
        driver.save()

        return redirect('driver_list')

    return render(request, 'driver_management/driver_edit.html', {'driver': driver})

def driver_delete(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    driver.delete()
    return redirect('driver_list')

def schedule_list(request):
    schedules = Schedule.objects.all()
    return render(request, 'schedule_management/schedule_list.html', {'schedules': schedules})

def schedule_add(request):
    if request.method == 'POST':
        time = request.POST.get('time')
        origin = request.POST.get('origin')
        destination = request.POST.get('destination')
        frequency = request.POST.get('frequency')

        Schedule.objects.create(
            time=time,
            origin=origin,
            destination=destination,
            frequency=frequency
        )

        return redirect('schedule_list')
    return render(request, 'schedule_management/schedule_add.html')

def schedule_edit(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)

    if request.method == 'POST':
        schedule.time = request.POST.get('time')
        schedule.origin = request.POST.get('origin')
        schedule.destination = request.POST.get('destination')
        schedule.frequency = request.POST.get('frequency')
        schedule.save()

        return redirect('schedule_list')

    return render(request, 'schedule_management/schedule_edit.html', {'schedule': schedule})

def schedule_delete(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    schedule.delete()
    return redirect('schedule_list')

def trip_list(request):
    trips = Trip.objects.annotate(aggregate_seats=Sum('reservations__seats')).order_by('date')
    return render(request, 'trip_management/trip_list.html', {'trips': trips})


def trip_add(request):
    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        driver_id = request.POST.get('driver_id')
        vehicle_id = request.POST.get('vehicle_id')
        passengers = request.POST.getlist('passengers')

        schedule = Schedule.objects.get(id=schedule_id)
        driver = Driver.objects.get(id=driver_id)
        vehicle = Vehicle.objects.get(id=vehicle_id)

        dates = generate_dates(schedule.time, schedule.frequency)
        for trip_date in dates:
            Trip.objects.create(
                schedule=schedule,
                date=trip_date,
                driver=driver,
                vehicle=vehicle,
                notes=f"Trip on {trip_date} from {schedule.origin} to {schedule.destination}"
            )

        return redirect('trip_list')
    schedules = Schedule.objects.all()
    drivers = Driver.objects.all()
    vehicles = Vehicle.objects.all()
    return render(request, 'trip_management/trip_add.html', {'schedules': schedules, 'drivers': drivers, 'vehicles': vehicles})

def trip_edit(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)

    if request.method == 'POST':
        date = request.POST.get('date')
        driver_id = request.POST.get('driver_id')
        vehicle_id = request.POST.get('vehicle_id')
        passengers = request.POST.getlist('passengers')
        status = request.POST.get('status')
        notes = request.POST.get('notes')

        trip.date = date
        trip.driver = Driver.objects.get(id=driver_id)
        trip.vehicle = Vehicle.objects.get(id=vehicle_id)
        trip.passengers.set(passengers)
        trip.status = status
        trip.notes = notes
        trip.save()

        return redirect('trip_list')

    drivers = Driver.objects.all()
    vehicles = Vehicle.objects.all()
    passengers = Passenger.objects.all()
    return render(request, 'trip_management/trip_edit.html', {
        'trip': trip,
        'drivers': drivers,
        'vehicles': vehicles,
        'passengers': passengers
    })

def trip_delete(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    trip.delete()
    return redirect('trip_list')

def trip_assign(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)

    if request.method == 'POST':
        driver_id = request.POST.get('driver_id')
        vehicle_id = request.POST.get('vehicle_id')
        passenger_ids = request.POST.getlist('passengers')
        seats_list = request.POST.getlist('seats')  # Pobieramy liczbę miejsc

        status = request.POST.get('status')
        notes = request.POST.get('notes')

        trip.driver = Driver.objects.get(id=driver_id) if driver_id else None
        trip.vehicle = Vehicle.objects.get(id=vehicle_id) if vehicle_id else None
        trip.status = status
        trip.notes = notes
        trip.save()

        # Aktualizujemy rezerwacje
        for passenger_id, seats in zip(passenger_ids, seats_list):
            passenger = Passenger.objects.get(id=passenger_id)
            seats = int(seats)
            # Tworzymy tyle rezerwacji, ile wskazano miejsc
            Reservation.objects.filter(trip=trip, passenger=passenger).delete()
            Reservation.objects.create(trip=trip, passenger=passenger, seats=seats)

        return redirect('trip_list')

    drivers = Driver.objects.all()
    vehicles = Vehicle.objects.all()
    passengers = Passenger.objects.all()
    reservations = Reservation.objects.filter(trip=trip)

    return render(request, 'trip_management/trip_assign.html', {
        'trip': trip,
        'drivers': drivers,
        'vehicles': vehicles,
        'passengers': passengers,
        'reservations': reservations,
    })


def new_reservation(request):

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        seats = int(request.POST.get('seats'))
        trip_id = request.POST.get('route')
        notes = request.POST.get('notes')

        # Znajdź lub utwórz pasażera
        passenger, created = Passenger.objects.get_or_create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
        )

        # Utwórz rezerwację
        trip = Trip.objects.get(id=trip_id)
        Reservation.objects.create(
            trip=trip,
            passenger=passenger,
            seats=seats,
            notes=notes,
        )

        return redirect('trip_list')

    available_trips = Trip.objects.filter(status='planned').order_by('date', 'schedule__time')
    return render(request, 'reservation_management/new_reservation.html', {'available_trips': available_trips})



def trip_reservations(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    reservations = Reservation.objects.filter(trip=trip)

    return render(request, 'reservation_management/reservation_list.html', {
        'trip': trip,
        'reservations': reservations,
    })


def get_trips_by_date(request):
    date = request.GET.get('date')
    trips = Trip.objects.filter(date=date, status="planned").order_by('schedule__time').values('id', 'schedule__origin', 'schedule__destination', 'schedule__time')
    return JsonResponse(list(trips), safe=False)

def get_reserved_passengers(request, trip_id):
    trip = Trip.objects.get(id=trip_id)
    reserved_passenger_ids = trip.reservations.order_by("passenger__first_name").values_list('passenger_id', flat=True)
    return JsonResponse({'reserved_passenger_ids': list(reserved_passenger_ids)})


def update_trip_statuses():
    current_time = now()

    # Update completed trips (dates in the past)
    Trip.objects.filter(date__lt=current_time.date()).update(status="completed")

    # Update trips in progress (within 3 hours from now)
    three_hours_later = current_time + timedelta(hours=3)

    Trip.objects.filter(
        Q(date=current_time.date()) &
        Q(schedule__time__gte=current_time.time()) &
        Q(schedule__time__lte=three_hours_later.time())
    ).update(status="in_progress")

    # Update future trips to "planned"
    Trip.objects.filter(date__gt=current_time.date()).update(status="planned")



def generate_dates(start_time, frequency):
    if isinstance(start_time, str):
        start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')  # Format datetime-local

    start_date = start_time.date()

    dates = []
    if frequency == "daily":
        dates = [start_date + timedelta(days=i) for i in range(7)]  # 7 dni
    elif frequency == "weekly":
        dates = [start_date + timedelta(weeks=i) for i in range(4)]  # 4 tygodnie
    elif frequency == "monthly":
        dates = [start_date + timedelta(days=30 * i) for i in range(3)]  # 3 miesiące
    elif frequency == "not-regular":
        dates = [start_date]
    return dates



