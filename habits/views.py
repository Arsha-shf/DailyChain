from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from .models import Habit
from .forms import HabitForm

@login_required
def habits(request):
    habits = Habit.objects.filter(user=request.user, is_active=True)
    return render(request, 'habits/habits.html', {'habits': habits})

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
