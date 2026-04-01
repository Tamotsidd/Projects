from django.http import JsonResponse
from appointments.models import Doctor


def get_doctors(request):
    """GET all doctors with optional filters."""
    doctors = Doctor.objects.filter(is_active=True)

    name           = request.GET.get('name')
    specialization = request.GET.get('specialization')
    hospital       = request.GET.get('hospital')
    location       = request.GET.get('location')

    if name:           doctors = doctors.filter(name__icontains=name)
    if specialization: doctors = doctors.filter(specialization__icontains=specialization)
    if hospital:       doctors = doctors.filter(hospital__icontains=hospital)
    if location:       doctors = doctors.filter(location__icontains=location)

    data = list(doctors.values(
        'id', 'name', 'specialization', 'years_experience',
        'available_days', 'hospital', 'location', 'phone', 'email'
    ))
    return JsonResponse(data, safe=False)


def get_doctor(request, doctor_id):
    """GET single doctor details."""
    try:
        d = Doctor.objects.get(id=doctor_id)
        return JsonResponse({
            'id':              d.id,
            'name':            d.name,
            'specialization':  d.specialization,
            'years_experience': d.years_experience,
            'available_days':  d.available_days,
            'hospital':        d.hospital,
            'location':        d.location,
            'phone':           d.phone,
            'email':           d.email,
        })
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Doctor not found'}, status=404)