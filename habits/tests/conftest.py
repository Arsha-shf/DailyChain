import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.utils import timezone
from habits.models import Habit, HabitLog

User = get_user_model()

# ASSUMPTION #1: email-based auth (USERNAME_FIELD = 'email'), per your Phase 1 spec.
# If your CustomUser still uses `username`, swap email= for username= in both
# create_user calls AND in client.login() calls below.

@pytest.fixture
def user(db):
    return User.objects.create_user(email="user@test.com", password="password")

@pytest.fixture
def second_user(db):
    return User.objects.create_user(email="second_user@test.com", password="password")

@pytest.fixture
def habit(user):
    # ASSUMPTION #2: field names are `frequency` + `times_per_week`, per your
    # Phase 2 spec, NOT `frequency_per_week` (which doesn't exist on the model
    # per that spec). If your real model differs, fix here only.
    return Habit.objects.create(
        user=user,
        name="Exercise",
        frequency="daily",
        times_per_week=3,
        is_active=True,
    )

@pytest.fixture
def second_user_habit(second_user):
    return Habit.objects.create(
        user=second_user,
        name="Reading",
        frequency="daily",
        times_per_week=2,
        is_active=True,
    )

@pytest.fixture
def client_logged_in(client, user):
    client.login(email="user@test.com", password="password")
    return client

@pytest.fixture
def second_client_logged_in(second_user):
    c = Client()
    c.login(email="second_user@test.com", password="password")
    return c

@pytest.fixture
def log_today(habit):
    return HabitLog.objects.create(
        habit=habit,
        date=timezone.now().date(),
        note="Completed a run",
    )

@pytest.fixture
def log_yesterday(habit):
    yesterday = timezone.now() - timezone.timedelta(days=1)
    return HabitLog.objects.create(
        habit=habit,
        date=yesterday.date(),
        note="Did some yoga",
    )
