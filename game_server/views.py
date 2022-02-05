# game_server/views.py
from django.shortcuts import redirect, render
from django.core.cache import cache

def index(request):
    return render(request, 'game_server/index.html', {})

def join_room(request):
    current_rooms = cache.get('current_rooms')
    new_room_id = 0

    print("Rooms that are available: %s" % current_rooms)

    if current_rooms:
        for i in current_rooms.keys():
            if current_rooms[i] < 2:
                return redirect("/room/{0}/".format(i))
        new_room_id = int(i) + 1
    
    return redirect("/room/{0}/".format(new_room_id))
    

def session(request, room_id):
    return render(request, 'game_server/chat.html', {
        'room_id': room_id
    })
