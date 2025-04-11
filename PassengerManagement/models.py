from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


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
    year = models.PositiveIntegerField()
    seats = models.PositiveIntegerField()
    review_date = models.DateField(null=True, blank=True)
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
    license_expiry = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Schedule(models.Model):
    time = models.DateTimeField()
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    frequency = models.CharField(
        max_length=50,
        choices=[
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
            ("not-regular", "Not regular"),
        ],
        default="daily",
    )

    def __str__(self):
        return self.origin + " - " + self.destination


class Trip(models.Model):
    date = models.DateField()
    schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE)
    vehicle = models.ForeignKey('Vehicle', on_delete=models.SET_NULL, null=True, blank=True)
    driver = models.ForeignKey('Driver', on_delete=models.SET_NULL, null=True, blank=True)
    passengers = models.ManyToManyField(
        Passenger,
        through='Reservation',
        related_name='trips'
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ('planned', 'Planned'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
            ('archived', 'Archived'),
        ],
        default='planned',
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Trip from {self.schedule.origin} to {self.schedule.destination}"

    def sync_passengers(self):
        """
        Synchronizuj `passengers` z danymi z `Reservation`.
        """
        self.passengers.set(Passenger.objects.filter(reservations__trip=self))


class Reservation(models.Model):
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name='reservations')
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='reservations')
    seats = models.PositiveIntegerField(default=1)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    payment_currency = models.CharField(
        max_length=3,
        choices=[
            ('PLN', 'Polski Złoty'),
            ('EUR', 'Euro'),
        ],
        default='PLN'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('paid', 'Opłacona'),
            ('not-paid', 'Nieopłacona'),
        ],
        default='not-paid'
    )
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('online', 'Płatność online'),
            ('bank_transfer_office', 'Przelew online w biurze (BLIK)'),
            ('bank_transfer_driver', 'Przelew online u kierowcy (BLIK)'),
            ('cash_office', 'Gotówka w biurze'),
            ('cash_driver', 'Gotówka u kierowcy'),
        ],
        blank=True,
        null=True
    )
    payment_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Rezerwacja dla {self.passenger} na {self.trip}"

    def clean(self):
        if self.payment_status == 'paid' and not self.payment_amount:
            raise ValidationError("Jeśli status płatności to 'paid', kwota płatności musi być większa od 0.")
        if self.payment_status == 'not-paid' and self.payment_amount > 0:
            raise ValidationError("Jeśli status płatności to 'not-paid', kwota płatności musi wynosić 0.")

    def save(self, *args, **kwargs):
        if self.payment_status == 'paid' and not self.payment_date:
            self.payment_date = timezone.now()
        if self.payment_status == 'not-paid':
            self.payment_amount = 0.0
            self.payment_currency = 'PLN'
            self.payment_method = None
        self.clean()
        super().save(*args, **kwargs)
