from django.urls import path
from .views import PrescriptionListView, PrescriptionDetailView



# prescription/urls.py — change to:
urlpatterns = [
    path('',          PrescriptionListView.as_view(),   name='prescription-list'),
    path('<int:pk>/', PrescriptionDetailView.as_view(), name='prescription-detail'),
]