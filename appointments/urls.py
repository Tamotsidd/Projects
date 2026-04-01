from django.urls import path
from .views import (
    DoctorListView,
    AvailableSlotsView,
    BookAppointmentView,
    AppointmentConfirmationView,
)

urlpatterns = [
    # Step 1 — load doctor cards
    path('doctors/',                        DoctorListView.as_view(),           name='doctor_list'),

    # Step 2 — check available time slots
    path('slots/',                          AvailableSlotsView.as_view(),        name='available_slots'),

    # Step 3 — submit booking
    path('book/',                           BookAppointmentView.as_view(),       name='book_appointment'),

    # Confirmation page
    path('confirmation/<str:booking_reference>/', AppointmentConfirmationView.as_view(), name='confirmation'),
]