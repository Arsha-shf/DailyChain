from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta

class FrequencyChoices(models.TextChoices):
    DAILY = 'daily', 'Daily'
    WEEKLY = 'weekly', 'Weekly'
    TIMES_PER_WEEK = 'times_per_week', 'X Times Per Week'

class Habit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=20, blank=True, null=True)
    times_per_week = models.PositiveIntegerField(blank=True, null=True)
    icon = models.CharField(max_length=20, blank=True, null=True)
    frequency = models.CharField(
        max_length=20,
        choices=FrequencyChoices.choices,
        default=FrequencyChoices.DAILY
    )

    def current_streak(self):
        dates = set(
            HabitLog.objects.filter(habit=self)
            .values_list('date', flat=True)
        )
        streak = 0
        current_day = date.today()

        while current_day in dates:
            streak+=1
            current_day -= timedelta(days=1)
        return streak

    def longest_streak(self):
        dates = sorted(
            HabitLog.objects.filter(habit=self)
            .values_list('date', flat=True)
        )
        if not dates:
            return 0
        current_streak = 1
        longest_streak = 1

        for i in range(1,( len(dates))):
            if dates[i] - dates[i-1] == timedelta(days=1):
                current_streak+=1
            else:
                current_streak=1
            if current_streak > longest_streak:
                longest_streak = current_streak
        return longest_streak

    class Meta:
        unique_together = ('user', 'name', 'frequency')

    def __str__(self):
        return self.name

class HabitLog(models.Model):
    habit = models.ForeignKey("Habit", verbose_name=_(""), on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_("Date"))

    class Meta:
        unique_together = ('habit', 'date')
