from django.contrib import admin
from .models import Doctor, Appointment


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display  = ['name', 'specialization', 'years_experience', 'available_days', 'is_active']
    list_filter   = ['specialization', 'is_active']
    search_fields = ['name', 'specialization']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display  = ['booking_reference', 'patient_name', 'doctor', 'appointment_date', 'appointment_time', 'status']
    list_filter   = ['status', 'appointment_date', 'doctor']
    search_fields = ['booking_reference', 'patient_name', 'patient_email']
    readonly_fields = ['booking_reference', 'created_at', 'updated_at']
    ordering      = ['-appointment_date']