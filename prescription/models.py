from django.db import models

class Prescription(models.Model):
    patient_name = models.CharField(max_length=100)
    doctor_name  = models.CharField(max_length=100)
    medication   = models.CharField(max_length=200)
    dosage       = models.CharField(max_length=100)
    frequency    = models.CharField(max_length=100)
    duration     = models.CharField(max_length=100)
    notes        = models.TextField(blank=True, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medication} → {self.patient_name}"

    class Meta:
        ordering = ['-created_at']