from django.shortcuts import render

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Message
from django.contrib.auth.models import User
import json

# SEND a message
@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        sender   = User.objects.get(id=data['sender_id'])
        receiver = User.objects.get(id=data['receiver_id'])

        message = Message.objects.create(
            sender=sender,
            receiver=receiver,
            message=data['message']
        )
        return JsonResponse({'message': 'Message sent!', 'id': message.id})


#GET chat history between two users
def chat_history(request, sender_id, receiver_id):
    messages = Message.objects.filter(
        sender_id=sender_id,
        receiver_id=receiver_id
    ) | Message.objects.filter(
        sender_id=receiver_id,
        receiver_id=sender_id
    )
    messages = messages.order_by('timestamp').values()
    return JsonResponse(list(messages), safe=False)


#MARK messages as read
@csrf_exempt
def mark_as_read(request, receiver_id, sender_id):
    Message.objects.filter(
        sender_id=sender_id,
        receiver_id=receiver_id,
        is_read=False
    ).update(is_read=True)
    return JsonResponse({'message': 'Messages marked as read!'})


#GET unread message count
def unread_count(request, receiver_id):
    count = Message.objects.filter(
        receiver_id=receiver_id,
        is_read=False
    ).count()
    return JsonResponse({'unread_count': count})
