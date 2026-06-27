from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from .models import Habit, HabitLog
from .forms import HabitForm
from datetime import date, timedelta
import json
from django.http import JsonResponse

@login_required
def habits(request):
    habits = Habit.objects.filter(user=request.user,is_active=True).order_by('order').prefetch_related('habitlog_set')
    today = date.today()
    completed_today = HabitLog.objects.filter(
        habit__user=request.user,
        date=today
    ).values_list('habit_id', flat=True)
    completed_count = completed_today.count()
    total_habits = habits.count()
    pending_count = total_habits - completed_count

    return render(request, 'habits/habits.html', {
        'habits': habits,
        'completed_today': completed_today,
        'pending_count': pending_count
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
        note = request.POST.get("note", "").strip()
        HabitLog.objects.create(habit=habit, date=today, note=note)
    return redirect('habits')

@login_required
def habit_detail(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    today = date.today()
    start_day = today - timedelta(days=83)
    days = [start_day + timedelta(days=i) for i in range(84)]
    logs = HabitLog.objects.filter(habit=habit, date__gte=start_day)
    logged_dates = {log.date: log.note for log in logs}
    return render(request, 'habits/habit_detail.html', {
        'habit': habit,
        'days': days,
        'logged_dates': logged_dates,
    })

    return render(
        request,
        'habits/habit_detail.html',
        {
            'habit': habit,
            'days': days,
            'logged_dates': logged_dates,
        }
    )

@login_required
def reorder_habits(request):
    if request.method == "POST":
        data = json.loads(request.body)
        habit_order = data["order"]

        for i, habit_id in enumerate(habit_order):
            try:
                habit = Habit.objects.get(id=habit_id, user=request.user)
                habit.order = i
                habit.save()
            except Habit.DoesNotExist:
                continue
        return JsonResponse({"status": "ok"})

@login_required
def archive_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    if request.method == 'POST':
        habit.is_active = False
        habit.save()
        return redirect('habits')
    return render(request, 'habits/archive_habit.html', {'habit': habit})

@login_required
def archived_habits(request):
    habits = Habit.objects.filter(
        user=request.user,
        is_active=False
    ).order_by("-created_at")
    return render(request, 'habits/archived_habits.html', {'habits':habits})

@login_required
def restore_habit(request, habit_id):
    habit = get_object_or_404(
        Habit,
        id=habit_id,
        user=request.user,
        is_active=False
    )
    habit.is_active = True
    habit.save()
    return redirect("archived_habits")
