from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import HealthRecord
import json

# 1. GET all health records of a patient
def get_patient_records(request, patient_id):
    records = HealthRecord.objects.filter(
        patient_id=patient_id
    ).values()
    return JsonResponse(list(records), safe=False)


# 2. ADD a new health record (doctor only)
@csrf_exempt
def add_record(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        record = HealthRecord.objects.create(
            patient_id=data['patient_id'],
            doctor_id=data['doctor_id'],
            diagnosis=data['diagnosis'],
            prescription=data.get('prescription', ''),
            report=data.get('report', ''),
            visit_date=data['visit_date'],
            notes=data.get('notes', '')
        )
        return JsonResponse({'message': 'Health record added!', 'id': record.id})


# 3. UPDATE a health record (doctor only)
@csrf_exempt
def update_record(request, record_id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        try:
            record = HealthRecord.objects.get(id=record_id)
            record.diagnosis   = data.get('diagnosis', record.diagnosis)
            record.prescription = data.get('prescription', record.prescription)
            record.report      = data.get('report', record.report)
            record.notes       = data.get('notes', record.notes)
            record.save()
            return JsonResponse({'message': 'Record updated!'})
        except HealthRecord.DoesNotExist:
            return JsonResponse({'error': 'Record not found'}, status=404)


# 4. GET single record details
def get_record(request, record_id):
    try:
        record = HealthRecord.objects.get(id=record_id)
        data = {
            'id': record.id,
            'patient_id': record.patient_id,
            'doctor_id': record.doctor_id,
            'diagnosis': record.diagnosis,
            'prescription': record.prescription,
            'report': record.report,
            'visit_date': str(record.visit_date),
            'notes': record.notes,
            'created_at': str(record.created_at),
        }
        return JsonResponse(data)
    except HealthRecord.DoesNotExist:
        return JsonResponse({'error': 'Record not found'}, status=404)