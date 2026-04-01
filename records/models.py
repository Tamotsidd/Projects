from django.db import models
from django.conf import settings  

class HealthRecord(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='health_records')
    doctor  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_records')
    diagnosis   = models.TextField()
    prescription = models.TextField(blank=True)
    report      = models.TextField(blank=True)
    visit_date  = models.DateField()
    notes       = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient} - {self.diagnosis} on {self.visit_date}"