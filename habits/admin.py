from django.contrib import admin
from .models import Habit, HabitLog

@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ['name',
                    'user',
                    'created_at',
                    'is_active',
                    'category',
                    'color',
                    'times_per_week',
                    'icon',
                    'frequency']

@admin.register(HabitLog)
class HabitLogAdmin(admin.ModelAdmin):
    list_display = ['habit', 'date']
