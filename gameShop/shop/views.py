# Django
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
# Use for restricting access on class-based views
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# Use for restricting access on method-based views
from django.contrib.auth.decorators import login_required

# Models
from .models import Game, GamePurchase #, AllHighScores
from users.models import Profile, DevProfile
from play_game.models import GameData


def home(request):
    return render(request, 'shop/index.html')

class GameListView(ListView):
    model = Game
    #template_name = '' # use if different than game_list.html
    #context_object_name = 'games' # name used in the template, default is 'object'
    #ordering = ['name'] # attribute(s) to order by, prepend with '-'sign to reverse


class GameDetailView(DetailView):
    model = Game

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        game = self.get_object()
        user = self.request.user
        is_purchased = user.is_authenticated and GamePurchase.objects.filter(user=user, game=game).first() != None
        times_purchased = len(GamePurchase.objects.filter(game=game))
        context['game_purchased'] = is_purchased
        context['times_purchased'] = times_purchased

        return context
        


class GameCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Game
    fields = ['name', 'description', 'price', 'source']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.profile.is_dev == True


class GameUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Game
    fields = ['name', 'description', 'price', 'source']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        is_dev = self.request.user.profile.is_dev
        is_owner = self.get_object().author == self.request.user
        return is_dev and is_owner


class GameDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Game
    success_url = '/home'

    def test_func(self):
        is_dev = self.request.user.profile.is_dev
        is_owner = self.get_object().author == self.request.user
        return is_dev and is_owner


@login_required
def buy_confirm(request, game_id):
    game = Game.objects.get(pk=game_id)
    if GamePurchase.objects.filter(user=request.user, game=game).first() != None or game.author == request.user:
        return redirect('game-detail', game_id)
        
    return render(request, 'shop/buy_game.html', {'game': game})

# TODO: move imports to top
from hashlib import md5
from urllib.parse import urlencode
import time


def buy(request, game_id):
    user = request.user
    game = Game.objects.get(pk=game_id)
    dev_info = DevProfile.objects.get(user=game.author)

    pid = str(game.pk) + str(user.pk) + '_' + str(time.time())
    sid = dev_info.seller_id
    amount = game.price
    success_url = request.build_absolute_uri(reverse('buy-success', kwargs={'game_id': game_id}))
    cancel_url = request.build_absolute_uri(reverse('game-detail', kwargs={'pk': game_id})) # 'http://localhost:8000/'
    error_url = request.build_absolute_uri(reverse('buy-error'))
    secret = dev_info.secret_key
    # use older style string formatting for compatibility with Python version < 3.6
    #checksumstr = f"pid={pid:s}&sid={sid:s}&amount={amount:.2f}&token={secret:s}"
    checksumstr = "pid={:s}&sid={:s}&amount={:.2f}&token={:s}".format(pid, sid, amount, secret)
    checksum = md5(checksumstr.encode('utf-8')).hexdigest()

    bankapi = 'https://tilkkutakki.cs.aalto.fi/payments/pay'
    query = urlencode({
    'pid': pid, 'sid': sid, 'amount': "{:.2f}".format(amount), # f'{amount:.2f}',
    'checksum': checksum,
    'success_url': success_url,
    'cancel_url': cancel_url,
    'error_url': error_url})
    return redirect(bankapi + '?' + query)



def buy_success(request, game_id):
    game = Game.objects.get(pk=game_id)
    pid = request.GET.get('pid', None)
    ref = request.GET.get('ref', None)
    result = request.GET.get('result', None)
    secret = DevProfile.objects.get(user=game.author).secret_key
    checksum = request.GET.get('checksum', None)

    # use older style string formatting for compatibility with Python version < 3.6
    #checksumstr = f"pid={pid:s}&ref={ref:s}&result={result:s}&token={secret:s}"
    checksumstr = "pid={:s}&ref={:s}&result={:s}&token={:s}".format(pid, ref, result, secret)
    expected_checksum = md5(checksumstr.encode('utf-8')).hexdigest()

    if checksum == expected_checksum:
        try:
            user = request.user
            GamePurchase.objects.create(user=user, game=game, purchase_price=game.price, purchase_id=pid, purchase_ref=ref)
            return render(request, 'shop/buy_success.html', {'game': game})
        except Exception:
            pass
    
    return redirect('buy-error')
    

def buy_error(request):
    return render(request, 'shop/buy_error.html')


def highscores(request):
    score = GameData.objects.order_by('highscore')[::-1]
    games = Game.objects.all()
    return render(request, 'shop/highscores_details.html', {'score': score, 'games':games})
