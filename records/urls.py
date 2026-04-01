from django.urls import path
from . import views

urlpatterns = [
    path('add/',                        views.add_record),
    path('patient/<int:patient_id>/',   views.get_patient_records),
    path('<int:record_id>/',            views.get_record),
    path('update/<int:record_id>/',     views.update_record),
]