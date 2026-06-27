from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta
from collections import Counter

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
        default=FrequencyChoices.DAILY)
    order = models.PositiveBigIntegerField(default=0)

    def get_log_dates(self):
        return sorted(log.date for log in self.habitlog_set.all())

    def current_streak(self):
        dates = set(self.get_log_dates())
        streak = 0
        current_day = date.today()

        while current_day in dates:
            streak+=1
            current_day -= timedelta(days=1)
        return streak

    def longest_streak(self):
        dates = self.get_log_dates()
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

    def total_completions(self):
        return len(self.get_log_dates())

    def success_rate(self):
        week_ago = date.today() - timedelta(days=7)
        completions = sum(
            1 for log_date in self.get_log_dates()
            if log_date >= week_ago
        )
        rate = (completions/7) * 100
        return round(min(rate, 100), 1)

    def best_day_of_week(self):
        dates = self.get_log_dates()
        weekdays=[]
        for log_date in dates:
            day = log_date.strftime("%A")
            weekdays.append(day)
        if not weekdays:
            return None
        weekdays_count = Counter(weekdays)
        return weekdays_count.most_common(1)[0][0]

    class Meta:
        unique_together = ('user', 'name', 'frequency')

    def __str__(self):
        return self.name

class HabitLog(models.Model):
    habit = models.ForeignKey("Habit", verbose_name=_(""), on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_("Date"))

    class Meta:
        unique_together = ('habit', 'date')

    def __str__(self):
        return f"{self.habit.name} — {self.date}"
