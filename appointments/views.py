from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import Appointment, Doctor
from .Serializers import (
    DoctorSerializer,
    AvailableSlotsSerializer,
    BookAppointmentSerializer,
    AppointmentConfirmationSerializer,
)


class DoctorListView(generics.ListAPIView):
    """
    GET /api/doctors/
    Returns all active doctors to populate the booking form doctor cards.
    Optional filter: ?specialization=Cardiology
    """
    serializer_class   = DoctorSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Doctor.objects.filter(is_active=True)
        specialization = self.request.query_params.get('specialization')
        if specialization:
            qs = qs.filter(specialization__icontains=specialization)
        return qs


class AvailableSlotsView(APIView):
    """
    GET /api/slots/?doctor_id=1&date=2026-03-20
    Returns all 8 time slots with available: true/false
    so the frontend can grey out already booked ones.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        serializer = AvailableSlotsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        slots = serializer.get_available_slots()
        return Response({'slots': slots})


class BookAppointmentView(APIView):
    """
    POST /api/book/
    No login required. Patient submits all 3 steps in one payload.

    Request body:
    {
        "doctor_id": 1,
        "appointment_date": "2026-03-20",
        "appointment_time": "09:00",
        "patient_name": "John Doe",
        "patient_email": "john@example.com",
        "patient_phone": "+977 9812345678",
        "reason": "Chest pain"         ← optional
    }

    Response:
    {
        "message": "Appointment booked successfully!",
        "confirmation": { ...all booking details... }
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = BookAppointmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment  = serializer.save()
        confirmation = AppointmentConfirmationSerializer(appointment)
        return Response({
            'message': 'Appointment booked successfully!',
            'confirmation': confirmation.data,
        }, status=status.HTTP_201_CREATED)


class AppointmentConfirmationView(APIView):
    """
    GET /api/confirmation/MC-A3F9B2/
    Fetch booking details by reference to render the confirmation page.
    """
    permission_classes = [AllowAny]

    def get(self, request, booking_reference):
        try:
            appointment = Appointment.objects.select_related('doctor').get(
                booking_reference=booking_reference
            )
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Booking not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = AppointmentConfirmationSerializer(appointment)
        return Response(serializer.data)