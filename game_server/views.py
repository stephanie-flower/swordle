# game_server/views.py
from django.shortcuts import render

def index(request):
    return render(request, 'game_server/index.html', {})

def session(request, room_id):
    return render(request, 'game_server/chat.html', {
        'room_id': room_id
    })
