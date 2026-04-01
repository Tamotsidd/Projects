from django.urls import path
from . import views

urlpatterns = [
    path('send/',                                    views.send_message),
    path('history/<int:sender_id>/<int:receiver_id>/', views.chat_history),
    path('read/<int:receiver_id>/<int:sender_id>/',  views.mark_as_read),
    path('unread/<int:receiver_id>/',                views.unread_count),
]