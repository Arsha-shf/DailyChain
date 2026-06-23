from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from .models import Habit, HabitLog
from .forms import HabitForm
from datetime import date, timedelta

@login_required
def habits(request):
    habits = Habit.objects.filter(user=request.user, is_active=True)
    today = date.today()
    completed_today = HabitLog.objects.filter(
        habit__user=request.user,
        date=today
    ).values_list('habit_id', flat=True)
    return render(request, 'habits/habits.html', {
        'habits': habits,
        'completed_today': completed_today
    })

@login_required
def create_habit(request):
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            try:
                habit.save()
                messages.success(request, 'Habit created successfully :)')
                return redirect('habits')
            except IntegrityError:
                form.add_error(None ,'You already have a habit with this name and frequency!')
    else:
        form = HabitForm()
    return render(request, 'habits/create_habit.html', {'form': form})

@login_required
def edit_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    if request.method == 'POST':
        form = HabitForm(request.POST, instance=habit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Habit edited successfully :)')
            return redirect('habits')
    else:
        form = HabitForm(instance=habit)
    return render(request, 'habits/edit_habit.html', {'form': form, 'habit_id': habit_id})

@login_required
def delete_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    if request.method == 'POST':
        habit.delete()
        messages.success(request, 'Habit deleted successfully :)')
        return redirect('habits')
    return render(request, 'habits/delete_habit.html', {'habit': habit})

@login_required
def toggle_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    today = date.today()
    log = HabitLog.objects.filter(habit=habit, date=today).first()
    if log:
        log.delete()
    else:
        HabitLog.objects.create(habit=habit, date=today)
    return redirect('habits')

@login_required
def habit_detail(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    today = date.today()
    start_day = today - timedelta(days=83)
    days = [
        start_day + timedelta(days=i)
        for i in range(84)
    ]
    logged_dates = set(
        HabitLog.objects.filter(
            habit=habit,
            date__gte=start_day
        ).values_list('date', flat=True)
    )

    return render(
        request,
        'habits/habit_detail.html',
        {
            'habit': habit,
            'days': days,
            'logged_dates': logged_dates,
        }
    )