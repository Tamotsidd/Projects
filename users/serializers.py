from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, PatientProfile, DoctorProfile


# ── Patient profile (nested inside register) ──────────────────────────────────

class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PatientProfile
        fields = ['date_of_birth', 'gender', 'blood_group', 'address']


# ── Doctor profile (nested inside register) ───────────────────────────────────

class DoctorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DoctorProfile
        fields = ['specialization', 'license_number', 'years_experience', 'available_days']


# ── Register serializer ───────────────────────────────────────────────────────

class RegisterSerializer(serializers.Serializer):
    # Common fields
    full_name        = serializers.CharField(max_length=150)
    phone            = serializers.CharField(max_length=20)
    email            = serializers.EmailField(required=False, allow_blank=True)
    password         = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)
    role             = serializers.ChoiceField(choices=['patient', 'doctor'])

    # Patient optional fields
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    gender        = serializers.ChoiceField(
                        choices=['male', 'female', 'other'],
                        required=False, allow_blank=True)
    blood_group   = serializers.CharField(required=False, allow_blank=True)
    address       = serializers.CharField(required=False, allow_blank=True)

    # Doctor required fields
    specialization   = serializers.CharField(required=False, allow_blank=True)
    license_number   = serializers.CharField(required=False, allow_blank=True)
    years_experience = serializers.IntegerField(required=False, default=0)
    available_days   = serializers.CharField(required=False, allow_blank=True)

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError('This phone number is already registered.')
        return value

    def validate(self, attrs):
        # Passwords must match
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})

        # Doctors must provide specialization and license
        if attrs['role'] == 'doctor':
            if not attrs.get('specialization'):
                raise serializers.ValidationError({'specialization': 'Required for doctor registration.'})
            if not attrs.get('license_number'):
                raise serializers.ValidationError({'license_number': 'Required for doctor registration.'})

        return attrs

    def create(self, validated_data):
        # Pull out profile fields
        role = validated_data['role']

        user = User.objects.create_user(
            phone     = validated_data['phone'],
            password  = validated_data['password'],
            full_name = validated_data['full_name'],
            email     = validated_data.get('email', ''),
            role      = role,
        )

        if role == 'patient':
            PatientProfile.objects.create(
                user          = user,
                date_of_birth = validated_data.get('date_of_birth'),
                gender        = validated_data.get('gender', ''),
                blood_group   = validated_data.get('blood_group', ''),
                address       = validated_data.get('address', ''),
            )
        elif role == 'doctor':
            DoctorProfile.objects.create(
                user             = user,
                specialization   = validated_data.get('specialization', ''),
                license_number   = validated_data.get('license_number', ''),
                years_experience = validated_data.get('years_experience', 0),
                available_days   = validated_data.get('available_days', ''),
            )

        return user


# ── Login serializer ──────────────────────────────────────────────────────────

class LoginSerializer(serializers.Serializer):
    phone    = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        phone    = attrs['phone']
        password = attrs['password']

        # Check user exists
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            raise serializers.ValidationError({'phone': 'No account found with this phone number.'})

        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError({'password': 'Incorrect password.'})

        # Check account is active
        if not user.is_active:
            raise serializers.ValidationError({'phone': 'This account has been deactivated.'})

        attrs['user'] = user
        return attrs


# ── User info serializer (returned after login/register) ─────────────────────

class UserSerializer(serializers.ModelSerializer):
    patient_profile = PatientProfileSerializer(read_only=True)
    doctor_profile  = DoctorProfileSerializer(read_only=True)

    class Meta:
        model  = User
        fields = ['id', 'full_name', 'phone', 'email', 'role',
                  'created_at', 'patient_profile', 'doctor_profile']