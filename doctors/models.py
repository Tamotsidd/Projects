from django.db import models

class Doctor(models.Model):
    name           = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    hospital       = models.CharField(max_length=100)
    location       = models.CharField(max_length=100)
    experience     = models.IntegerField()  # years of experience
    phone          = models.CharField(max_length=20)
    email          = models.EmailField()
    is_available   = models.BooleanField(default=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.specialization} at {self.hospital}"
