from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

def load(request, player_id, game_id):
    #Should decide where gamestate models are held that these views process?
    return HttpResponse("Loading the game")

def save(request, player_id, game_id):
    #Should decide where gamestate models are held that these views process?
    return HttpResponse("Saving the game")

def play(request):
    return render(request, 'play_game/play.html')