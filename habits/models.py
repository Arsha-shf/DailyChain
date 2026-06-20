from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

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

    def __str__(self):
        return self.name

class HabitLog(models.Model):
    habit = models.ForeignKey("Habit", verbose_name=_(""), on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_("Date"))

    class Meta:
        unique_together = ('habit', 'date')
