from rest_framework import serializers
from django.utils import timezone
from .models import Appointment, Doctor, TIME_SLOTS


# ── 1. Doctor list serializer (populates Step 1 doctor cards) ─────────────────

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Doctor
        fields = ['id', 'name', 'specialization', 'years_experience', 'available_days']


# ── 2. Available slots serializer (populates Step 2 time grid) ────────────────

class AvailableSlotsSerializer(serializers.Serializer):
    doctor_id = serializers.IntegerField()
    date      = serializers.DateField()

    def validate_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError('Date cannot be in the past.')
        return value

    def validate_doctor_id(self, value):
        if not Doctor.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError('Doctor not found.')
        return value

    def get_available_slots(self):
        doctor_id = self.validated_data['doctor_id']
        date      = self.validated_data['date']

        # Get already booked times for this doctor on this date
        booked = Appointment.objects.filter(
            doctor_id=doctor_id,
            appointment_date=date,
            status__in=[Appointment.PENDING, Appointment.CONFIRMED]
        ).values_list('appointment_time', flat=True)

        return [
            {
                'time':      slot[0],
                'label':     slot[1],
                'available': slot[0] not in booked
            }
            for slot in TIME_SLOTS
        ]


# ── 3. Booking serializer (handles the full form submission) ──────────────────

class BookAppointmentSerializer(serializers.Serializer):
    # Step 1
    doctor_id = serializers.IntegerField()

    # Step 2
    appointment_date = serializers.DateField()
    appointment_time = serializers.ChoiceField(choices=[s[0] for s in TIME_SLOTS])

    # Step 3
    patient_name  = serializers.CharField(max_length=150)
    patient_email = serializers.EmailField()
    patient_phone = serializers.CharField(max_length=20)
    reason        = serializers.CharField(required=False, allow_blank=True)

    def validate_doctor_id(self, value):
        if not Doctor.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError('Doctor not found.')
        return value

    def validate_appointment_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError('Appointment date cannot be in the past.')
        return value

    def validate(self, attrs):
        doctor_id = attrs['doctor_id']
        date      = attrs['appointment_date']
        time      = attrs['appointment_time']

        # Check slot is not already taken
        if Appointment.objects.filter(
            doctor_id=doctor_id,
            appointment_date=date,
            appointment_time=time,
            status__in=[Appointment.PENDING, Appointment.CONFIRMED]
        ).exists():
            raise serializers.ValidationError({
                'appointment_time': 'This time slot is already booked. Please choose another.'
            })

        return attrs

    def create(self, validated_data):
        doctor = Doctor.objects.get(id=validated_data['doctor_id'])
        return Appointment.objects.create(
            doctor           = doctor,
            appointment_date = validated_data['appointment_date'],
            appointment_time = validated_data['appointment_time'],
            patient_name     = validated_data['patient_name'],
            patient_email    = validated_data['patient_email'],
            patient_phone    = validated_data['patient_phone'],
            reason           = validated_data.get('reason', ''),
        )


# ── 4. Confirmation serializer (drives the confirmation page) ─────────────────

class AppointmentConfirmationSerializer(serializers.ModelSerializer):
    doctor_name    = serializers.CharField(source='doctor.name', read_only=True)
    specialization = serializers.CharField(source='doctor.specialization', read_only=True)
    time_label     = serializers.SerializerMethodField()

    class Meta:
        model  = Appointment
        fields = [
            'booking_reference',
            'doctor_name',
            'specialization',
            'appointment_date',
            'appointment_time',
            'time_label',
            'patient_name',
            'patient_email',
            'patient_phone',
            'reason',
            'status',
            'created_at',
        ]

    def get_time_label(self, obj):
        return dict(TIME_SLOTS).get(obj.appointment_time, obj.appointment_time)