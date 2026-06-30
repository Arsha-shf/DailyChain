import pytest
from django.urls import reverse
from habits.models import HabitLog
from django.utils import timezone
import json


@pytest.mark.django_db
def test_toggle_habit_check_in_then_out(client_logged_in, habit):
    response = client_logged_in.post(reverse('habit-toggle', args=[habit.id]))
    assert response.status_code in (200, 302)  # CONFIRM actual: AJAX=200, normal POST=302
    assert HabitLog.objects.filter(habit=habit, date=timezone.now().date()).exists()

    response = client_logged_in.post(reverse('habit-toggle', args=[habit.id]))
    assert response.status_code in (200, 302)
    assert not HabitLog.objects.filter(habit=habit, date=timezone.now().date()).exists()


@pytest.mark.django_db
def test_toggle_habit_saves_note(client_logged_in, habit):
    response = client_logged_in.post(reverse('habit-toggle', args=[habit.id]), {
        'note': 'Felt great today',
    })
    log = HabitLog.objects.get(habit=habit, date=timezone.now().date())
    assert log.note == 'Felt great today'


@pytest.mark.django_db
def test_archive_habit(client_logged_in, habit):
    response = client_logged_in.post(reverse('habit-archive', args=[habit.id]))
    assert response.status_code in (200, 302)
    habit.refresh_from_db()
    assert not habit.is_active


@pytest.mark.django_db
def test_restore_habit(client_logged_in, habit):
    habit.is_active = False
    habit.save()
    response = client_logged_in.post(reverse('habit-restore', args=[habit.id]))
    assert response.status_code in (200, 302)
    habit.refresh_from_db()
    assert habit.is_active


@pytest.mark.django_db
def test_reorder_habits(client_logged_in, habit, user):
    from habits.models import Habit
    habit2 = Habit.objects.create(user=user, name="Reading", frequency="daily", times_per_week=2)
    response = client_logged_in.post(
        reverse('habit-reorder'),
        data=json.dumps({'order': [habit2.id, habit.id]}),
        content_type='application/json',
    )
    assert response.status_code == 200
    habit.refresh_from_db()
    habit2.refresh_from_db()
    assert habit2.order < habit.order


@pytest.mark.django_db
def test_reorder_habits_rejects_other_users_habit_id(client_logged_in, second_user_habit):
    response = client_logged_in.post(
        reverse('habit-reorder'),
        data=json.dumps({'order': [second_user_habit.id]}),
        content_type='application/json',
    )
    assert response.status_code in (400, 403, 404)
