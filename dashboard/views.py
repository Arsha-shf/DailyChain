from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from . import quotes
from datetime import datetime

@login_required
def dashboard_home(request):
    context = {
        'name': request.user.email.split('@')[0],
        'greeting':
            "Good morning" if datetime.now().hour < 12 else
            "Good afternoon" if datetime.now().hour < 18 else
            "Good evening",
        'last_login': request.user.last_login,
        'random_quote': quotes.get_random_quote()
    }
    return render(request, 'dashboard/home.html', context)
