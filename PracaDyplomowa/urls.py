"""
URL configuration for PracaDyplomowa project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from PassengerManagement import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('passengers/', views.passenger_list, name='passenger_list'),
    path('passengers/add/', views.passenger_add, name='passenger_add'),
    path('passengers/edit/<int:passenger_id>/', views.passenger_edit, name='passenger_edit'),
    path('passengers/delete/<int:passenger_id>/', views.passenger_delete, name='passenger_delete'),
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/add/', views.vehicle_add, name='vehicle_add'),
    path('vehicles/edit/<int:vehicle_id>/', views.vehicle_edit, name='vehicle_edit'),
    path('vehicles/delete/<int:vehicle_id>/', views.vehicle_delete, name='vehicle_delete'),
    path('drivers/', views.driver_list, name='driver_list'),
    path('drivers/add/', views.driver_add, name='driver_add'),
    path('drivers/edit/<int:driver_id>/', views.driver_edit, name='driver_edit'),
    path('drivers/delete/<int:driver_id>/', views.driver_delete, name='driver_delete'),
    path('schedules/', views.schedule_list, name='schedule_list'),
    path('schedules/add/', views.schedule_add, name='schedule_add'),
    path('schedules/edit/<int:schedule_id>/', views.schedule_edit, name='schedule_edit'),
    path('schedules/delete/<int:schedule_id>/', views.schedule_delete, name='schedule_delete'),
    path('trips/', views.trip_list, name='trip_list'),
    path('trips/add/', views.trip_add, name='trip_add'),
    path('trips/edit/<int:trip_id>/', views.trip_edit, name='trip_edit'),
    path('trips/delete/<int:trip_id>/', views.trip_delete, name='trip_delete'),
    path('trips/assign/<int:trip_id>/', views.trip_assign, name='trip_assign'),
    path('new_reservation/', views.new_reservation, name='new_reservation'),
    path('trips/<int:trip_id>/reservations/', views.trip_reservations, name='reservation_list'),
    path('trips/<int:trip_id>/reserved_passengers/', views.get_reserved_passengers, name='reserved_passengers'),
    path('get_trips_by_date/', views.get_trips_by_date, name='get_trips_by_date'),
    path("reports/general/", views.general_report_view, name="general_report"),
    path("reports/weekly/", views.weekly_report_view, name="weekly_report"),
]
