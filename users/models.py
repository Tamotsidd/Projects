
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):

    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('Phone number is required.')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    PATIENT = 'patient'
    DOCTOR  = 'doctor'
    ADMIN   = 'admin'

    ROLE_CHOICES = [
        (PATIENT, 'Patient'),
        (DOCTOR,  'Doctor'),
        (ADMIN,   'Admin'),
    ]

    phone      = models.CharField(max_length=20, unique=True)  # used to login
    full_name  = models.CharField(max_length=150)
    email      = models.EmailField(blank=True)
    role       = models.CharField(max_length=10, choices=ROLE_CHOICES, default=PATIENT)
    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    # Phone is used instead of username to login
    USERNAME_FIELD  = 'phone'
    REQUIRED_FIELDS = ['full_name', 'role']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.full_name} ({self.role}) — {self.phone}"


class PatientProfile(models.Model):
    BLOOD_GROUPS = [
        ('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
        ('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-'),
    ]
    user          = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    gender        = models.CharField(max_length=10, blank=True,
                                     choices=[('male','Male'),('female','Female'),('other','Other')])
    blood_group   = models.CharField(max_length=5, blank=True, choices=BLOOD_GROUPS)
    address       = models.TextField(blank=True)

    class Meta:
        db_table = 'patient_profiles'

    def __str__(self):
        return f"Patient: {self.user.full_name}"


class DoctorProfile(models.Model):
    user             = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization   = models.CharField(max_length=150)
    license_number   = models.CharField(max_length=50, unique=True)
    years_experience = models.PositiveIntegerField(default=0)
    available_days   = models.CharField(max_length=100, blank=True, help_text='e.g. Mon, Wed, Fri')

    class Meta:
        db_table = 'doctor_profiles'

    def __str__(self):
        return f"Dr. {self.user.full_name} — {self.specialization}"