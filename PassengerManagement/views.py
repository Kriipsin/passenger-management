from dataclasses import replace

from django.shortcuts import render, redirect, get_object_or_404
from reportlab.lib import colors

from .models import Passenger, Vehicle, Driver, Schedule, Trip, Reservation
from datetime import timedelta, datetime, date
from django.utils import timezone
from django.utils.timezone import localtime, localdate, now
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ValidationError
import matplotlib.pyplot as plt
from django.db.models import Sum, Count, F
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from reportlab.lib.pagesizes import A4


def home(request):
    in_progress_trips = Trip.objects.filter(status="in_progress")

    grouped_trips = (
        in_progress_trips
        .values("schedule__origin", "schedule__destination", "schedule__time")  # Grupowanie po polach
        .annotate(total_passengers=Sum("reservations__seats"))  # Sumowanie liczby miejsc
        .order_by("schedule__origin", "schedule__destination")  # Opcjonalne sortowanie
    )

    data = []
    for group in grouped_trips:
        data.append({
            "origin": group["schedule__origin"],
            "destination": group["schedule__destination"],
            "departure_time": str(group["schedule__time"])[11:16],
            "total_passengers": group["total_passengers"] or 0,
            "trip_id": in_progress_trips.filter(
                schedule__origin=group["schedule__origin"],
                schedule__destination=group["schedule__destination"],
                schedule__time=group["schedule__time"],
            ).first().id
        })

    return render(request, "home.html", {
        "data": data,
    })

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
        active = 'active' in request.POST or True
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
    update_trip_statuses()  # Aktualizacja statusów kursów

    trips = Trip.objects.annotate(
        total_passengers=Sum('reservations__seats')
    ).order_by('date', 'schedule__time')

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

        # Pobierz dane pasażerów i rezerwacji z formularza
        passenger_ids = request.POST.getlist('passengers')
        seats_data = request.POST.getlist('seats')
        seats_data = [seat for seat in seats_data if seat]
        payment_status_data = request.POST.getlist('payment_status')
        payment_status_data = [status for status in payment_status_data if status == 'paid']
        payment_amount_data = request.POST.getlist('payment_amount')
        #convert to float
        payment_amount_data = [float(amount.replace(',','.')) for amount in payment_amount_data if amount]
        payment_currency_data = request.POST.getlist('payment_currency')
        payment_method_data = request.POST.getlist('payment_method')

        # Aktualizuj dane kursu
        trip.driver = Driver.objects.get(id=driver_id) if driver_id else None
        trip.vehicle = Vehicle.objects.get(id=vehicle_id) if vehicle_id else None
        trip.status = request.POST.get('status') or trip.status or 'planned'
        trip.notes = request.POST.get('notes') or trip.notes or ''

        trip.save()

        # Aktualizuj rezerwacje
        for i, passenger_id in enumerate(passenger_ids):

            passenger = Passenger.objects.get(id=passenger_id)
            Reservation.objects.update_or_create(
                trip=trip,
                passenger=passenger,
                defaults={
                    'seats': int(seats_data[i]) if seats_data[i] else 1,
                    'payment_status': payment_status_data[i],
                    'payment_amount': float(payment_amount_data[i]) if payment_status_data[i] == 'paid' else 0.0,
                    'payment_currency': payment_currency_data[i] if payment_status_data[i] == 'paid' else None,
                    'payment_method': payment_method_data[i] if payment_status_data[i] == 'paid' else None,
                }
            )

        return redirect('trip_list')

        # Pobierz istniejące rezerwacje
    reservations = Reservation.objects.filter(trip=trip)
    passenger_reservations = {
        reservation.passenger.id: {
            'first_name': reservation.passenger.first_name,
            'last_name': reservation.passenger.last_name,
            'seats': reservation.seats,
            'payment_status': reservation.payment_status,
            'payment_amount': float(reservation.payment_amount) if reservation.payment_amount else 0.00,
            'payment_currency': reservation.payment_currency,
            'payment_method': reservation.payment_method,
        }
        for reservation in reservations
    }

    # passenger_reservations = passenger_reservations or {}

    print(passenger_reservations)


    return render(request, 'trip_management/trip_assign.html', {
        'trip': trip,
        'drivers': Driver.objects.all(),
        'vehicles': Vehicle.objects.all(),
        'passengers': Passenger.objects.all(),
        'passenger_reservations': passenger_reservations,
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
        payment_status = request.POST.get('payment_status', 'not-paid')
        payment_amount = request.POST.get('payment_amount', '0.0')
        payment_currency = request.POST.get('payment_currency', 'PLN')
        payment_method = request.POST.get('payment_method', '')

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
            payment_status=payment_status,
            payment_amount=payment_amount if payment_status == 'paid' else 0.0,
            payment_currency=payment_currency if payment_status == 'paid' else 'PLN',
            payment_method=payment_method if payment_status == 'paid' else None,
            notes=notes,
        )

        return redirect('trip_list')

    # Pobierz dostępne trasy
    today = localdate()
    available_trips = Trip.objects.filter(date__gte=today, status="planned").order_by('date', 'schedule__time')


    return render(request, 'reservation_management/new_reservation.html', {'available_trips': available_trips})

def trip_reservations(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    reservations = Reservation.objects.filter(trip=trip)

    return render(request, 'reservation_management/reservation_list.html', {
        'trip': trip,
        'reservations': reservations,
    })

def get_trips_by_date(request):
    date_str = request.GET.get('date')
    trips = Trip.objects.filter(date=date_str, status__in=["planned", "in_progress"]).order_by('schedule__time').select_related('schedule')
    print(f"Zapytanie dla daty: {date_str}, znalezione przejazdy: {trips}")
    if not trips.exists():
        return JsonResponse({'error': 'No trips found for this date'}, status=404)
    return JsonResponse(list(trips.values('id', 'schedule__origin', 'schedule__destination', 'schedule__time')), safe=False)

def get_reserved_passengers(request, trip_id):
    trip = Trip.objects.get(id=trip_id)
    reserved_passenger_ids = trip.reservations.order_by("passenger__first_name").values_list('passenger_id', flat=True)
    return JsonResponse({'reserved_passenger_ids': list(reserved_passenger_ids)})

def update_trip_statuses():
    now = localtime(timezone.now())

    # Kursy w przeszłości - "completed"
    Trip.objects.filter(
        date__lt=now.date()
    ).update(status='completed', notes='Kurs zakończony.')

    # Kursy dzisiejsze - "in_progress"
    ongoing_trips = Trip.objects.filter(
        date=now.date(),
    )
    ongoing_trips.update(status='in_progress')

    # Pozostałe kursy jako "planned"
    Trip.objects.filter(
        date__gte=now.date(),
        status__in=['completed', 'in_progress']
    ).exclude(id__in=ongoing_trips.values_list('id', flat=True)).update(status='planned')

def validate_driver_and_vehicle_availability(driver_id, vehicle_id, trip):
    """
    Sprawdza, czy kierowca i pojazd spełniają warunki:
    - Maksymalnie 4 kursy dziennie.
    - Co najmniej 2 godziny i 15 minut przerwy między kursami.
    """
    date = trip.date
    time = trip.schedule.time

    # Kursy dla danego kierowcy i pojazdu tego samego dnia
    driver_trips = Trip.objects.filter(driver_id=driver_id, date=date).exclude(id=trip.id)
    vehicle_trips = Trip.objects.filter(vehicle_id=vehicle_id, date=date).exclude(id=trip.id)

    # Sprawdzenie liczby kursów
    if driver_trips.count() >= 4:
        raise ValidationError(f"Kierowca może obsłużyć maksymalnie 4 kursy dziennie.")
    if vehicle_trips.count() >= 4:
        raise ValidationError(f"Pojazd może być przypisany maksymalnie do 4 kursów dziennie.")

    # Sprawdzenie czasu przerwy między kursami
    for t in driver_trips:
        if abs((time - t.schedule.time).total_seconds()) < 2 * 3600 + 15 * 60:
            raise ValidationError(f"Kierowca potrzebuje co najmniej 2h i 15min przerwy między kursami.")
    for t in vehicle_trips:
        if abs((time - t.schedule.time).total_seconds()) < 2 * 3600 + 15 * 60:
            raise ValidationError(f"Pojazd potrzebuje co najmniej 2h i 15min przerwy między kursami.")

def generate_dates(start_time, frequency):
    if isinstance(start_time, str):
        start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')  # Format datetime-local

    start_date = start_time.date()

    dates = []
    if frequency == "daily":
        dates = [start_date + timedelta(days=i) for i in range(7)]
    elif frequency == "weekly":
        dates = [start_date + timedelta(weeks=i) for i in range(4)]
    elif frequency == "monthly":
        dates = [start_date + timedelta(days=30 * i) for i in range(3)]
    elif frequency == "not-regular":
        dates = [start_date]
    return dates

def generate_report(report_type='general', filename='report.pdf'):
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', './static/fonts/DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', './static/fonts/DejaVuSans-Bold.ttf'))

        # Dane źródłowe
        if report_type == 'weekly':
            start_of_week = now().date() - timedelta(days=now().weekday())
            trips = Trip.objects.filter(status='completed', date__gte=start_of_week)
        else:
            trips = Trip.objects.filter(status='completed')

        total_income = trips.aggregate(total=Sum('reservations__payment_amount'))['total'] or 0
        weeks = trips.values('date__week').distinct().count()
        weekly_avg_income = float(total_income / weeks) if weeks else 0

        day_data = trips.values('date__week_day').annotate(
            passengers=Count('reservations__passenger'),
            income=Sum('reservations__payment_amount')
        )

        # Dane wykresowe
        days = ['Pon', 'Wt', 'Sr', 'Czw', 'Pt', 'Sob', 'Nd']
        passengers_by_day = [0.0] * 7
        income_by_day = [0.0] * 7

        for data in day_data:
            day_index = (data['date__week_day'] - 2) % 7
            passengers_by_day[day_index] += float(data.get('passengers') or 0)
            income_by_day[day_index] += float(data.get('income') or 0)

        if report_type == 'general':
            trips_count = trips.count()
            if trips_count > 0:
                passengers_by_day = [p / trips_count for p in passengers_by_day]
                income_by_day = [i / trips_count for i in income_by_day]

        # Metody płatności
        payment_methods = dict(Reservation._meta.get_field('payment_method').choices)
        payment_data = {
            payment_methods.get(key, 'Inna'): trips.filter(reservations__payment_method=key).count()
            for key in payment_methods
        }

        # PDF
        pdf = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        margin = 50
        y = height - margin

        pdf.setFont("DejaVuSans-Bold", 16)
        pdf.drawString(margin, y, f"Raport {'ogólny' if report_type == 'general' else 'tygodniowy'}")
        pdf.setFont("DejaVuSans", 10)
        y -= 20
        pdf.drawString(margin, y, f"Data generowania: {now().strftime('%d-%m-%Y %H:%M:%S')}")

        y -= 30
        pdf.setFont("DejaVuSans-Bold", 12)
        pdf.drawString(margin, y, "Podsumowanie:")
        pdf.setFont("DejaVuSans", 10)
        y -= 15
        pdf.drawString(margin, y, f"- Liczba przejazdów: {trips.count()}")
        y -= 15
        pdf.drawString(margin, y, f"- Całkowity dochód: {total_income:.2f} PLN")
        y -= 15
        if report_type == 'general':
            pdf.drawString(margin, y, f"- Średni dochód tygodniowy: {weekly_avg_income:.2f} PLN")

        # Wykres pasażerów
        y -= 40
        pdf.setFont("DejaVuSans-Bold", 12)
        pdf.drawString(margin, y, "Średnia liczba pasażerów wg dnia tygodnia")
        y -= 10
        d = Drawing(400, 150)
        bar1 = VerticalBarChart()
        bar1.x = 0
        bar1.y = 0
        bar1.height = 120
        bar1.width = 350
        bar1.data = [passengers_by_day]
        bar1.categoryAxis.categoryNames = days
        bar1.bars.fillColor = colors.HexColor("#4F81BD")
        d.add(bar1)
        d.drawOn(pdf, margin, y - 130)

        # Wykres zarobków
        y -= 180
        pdf.setFont("DejaVuSans-Bold", 12)
        pdf.drawString(margin, y, "Średni dochód wg dnia tygodnia (PLN)")
        y -= 10
        d = Drawing(400, 150)
        bar2 = VerticalBarChart()
        bar2.x = 0
        bar2.y = 0
        bar2.height = 120
        bar2.width = 350
        bar2.data = [income_by_day]
        bar2.categoryAxis.categoryNames = days
        bar2.bars.fillColor = colors.HexColor("#9BBB59")
        d.add(bar2)
        d.drawOn(pdf, margin, y - 130)

        # Wykres kołowy - metody płatności
        y -= 180
        pdf.setFont("DejaVuSans-Bold", 12)
        pdf.drawString(margin, y, "Podział metod płatności")
        y -= 10
        d = Drawing(200, 150)
        pie = Pie()
        pie.x = 100
        pie.y = -55
        pie.data = list(payment_data.values())
        pie.labels = list(payment_data.keys())
        pie.width = 150
        pie.height = 150
        pie.slices.fontName = "DejaVuSans"
        pie.slices.fontSize = 8
        d.add(pie)
        d.drawOn(pdf, margin, y - 130)

        pdf.save()

    except Exception as e:
        print(f"Błąd podczas generowania raportu: {e}")

def general_report_view(request):
    generate_report(report_type='general')
    with open("report.pdf", "rb") as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="general_report.pdf"'
        return response


def weekly_report_view(request):
    generate_report(report_type='weekly')
    with open("report.pdf", "rb") as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="weekly_report.pdf"'
        return response