from django.contrib import admin
from .models import Prescription

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display  = ['medication', 'patient_name', 'doctor_name', 'dosage', 'created_at']
    search_fields = ['patient_name', 'doctor_name', 'medication']
    readonly_fields = ['created_at']