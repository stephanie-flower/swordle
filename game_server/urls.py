# game_server/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('join_room/', views.join_room, name="join_room"),
    path('<str:room_id>/', views.session, name='session')
]
