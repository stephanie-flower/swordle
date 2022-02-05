# game_server/views.py
from django.shortcuts import render

def index(request):
    return render(request, 'game_server/index.html', {})

def game(request, game_name):
    return render(request, 'game_server/game.html', {
        'game_name': game_name
    })