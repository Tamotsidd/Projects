from django.urls import path
from . import views

urlpatterns = [
    path('',                  views.get_doctors),
    path('<int:doctor_id>/',  views.get_doctor),
]