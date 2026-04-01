import uuid
from django.db import models


TIME_SLOTS = [
    ('09:00', '9:00 AM'),
    ('09:30', '9:30 AM'),
    ('10:00', '10:00 AM'),
    ('10:30', '10:30 AM'),
    ('11:00', '11:00 AM'),
    ('11:30', '11:30 AM'),
    ('13:00', '1:00 PM'),
    ('13:30', '1:30 PM'),
]


class Doctor(models.Model):
    """
    Merged Doctor model — combines your booking fields
    with teammate's hospital/location/contact fields.
    """
    name             = models.CharField(max_length=150)
    specialization   = models.CharField(max_length=150)
    years_experience = models.PositiveIntegerField(default=0)
    available_days   = models.CharField(max_length=100, help_text='e.g. Mon, Wed, Fri')

    # From teammate's doctors app
    hospital  = models.CharField(max_length=150, blank=True)
    location  = models.CharField(max_length=150, blank=True)
    phone     = models.CharField(max_length=20, blank=True)
    email     = models.EmailField(blank=True)

    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'doctors'

    def __str__(self):
        return f"Dr. {self.name} — {self.specialization}"


class Appointment(models.Model):
    PENDING   = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'

    STATUS_CHOICES = [
        (PENDING,   'Pending'),
        (CONFIRMED, 'Confirmed'),
        (CANCELLED, 'Cancelled'),
        (COMPLETED, 'Completed'),
    ]

    booking_reference = models.CharField(max_length=12, unique=True, editable=False)
    doctor            = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date  = models.DateField()
    appointment_time  = models.CharField(max_length=5, choices=TIME_SLOTS)
    patient_name      = models.CharField(max_length=150)
    patient_email     = models.EmailField()
    patient_phone     = models.CharField(max_length=20)
    reason            = models.TextField(blank=True)
    status            = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    notes             = models.TextField(blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'appointments'
        ordering        = ['-appointment_date', '-appointment_time']
        unique_together = ['doctor', 'appointment_date', 'appointment_time']

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = 'MC-' + uuid.uuid4().hex[:6].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.booking_reference}] {self.patient_name} → Dr. {self.doctor.name} on {self.appointment_date}"