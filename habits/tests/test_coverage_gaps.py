import pytest
from django.urls import reverse
from django.db import IntegrityError
from django.utils import timezone
from freezegun import freeze_time
from habits.models import Habit, HabitLog
from habits.forms import HabitForm

# ---------------------------------------------------------------------------
# 1. archived_habits view — never directly tested before
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_archived_habits_shows_only_inactive(client_logged_in, habit, user):
    archived = Habit.objects.create(
        user=user, name="Old habit", frequency="daily",
        times_per_week=1, is_active=False,
    )
    response = client_logged_in.get(reverse('archived-habits'))
    assert response.status_code == 200
    names = [h.name for h in response.context['habits']]
    assert archived.name in names
    assert habit.name not in names  # habit fixture is active, shouldn't show


@pytest.mark.django_db
def test_archived_habits_excludes_other_users(client_logged_in, second_user):
    other_archived = Habit.objects.create(
        user=second_user, name="Not mine", frequency="daily",
        times_per_week=1, is_active=False,
    )
    response = client_logged_in.get(reverse('archived-habits'))
    names = [h.name for h in response.context['habits']]
    assert other_archived.name not in names


@pytest.mark.django_db
def test_anonymous_redirect_archived_habits(client):
    response = client.get(reverse('archived-habits'))
    assert response.status_code == 302
    assert "login" in response.url


# ---------------------------------------------------------------------------
# 2. GET branches for delete/archive confirmation pages
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_delete_habit_get_shows_confirm_page(client_logged_in, habit):
    response = client_logged_in.get(reverse('habit-delete', args=[habit.id]))
    assert response.status_code == 200
    assert response.context['habit'].id == habit.id
    # habit must NOT be deleted by a GET request
    assert Habit.objects.filter(id=habit.id).exists()


@pytest.mark.django_db
def test_archive_habit_get_shows_confirm_page(client_logged_in, habit):
    response = client_logged_in.get(reverse('habit-archive', args=[habit.id]))
    assert response.status_code == 200
    assert response.context['habit'].id == habit.id
    habit.refresh_from_db()
    # habit must still be active, GET should not archive it
    assert habit.is_active


@pytest.mark.django_db
def test_other_user_cannot_get_delete_confirm_page(second_client_logged_in, habit):
    response = second_client_logged_in.get(reverse('habit-delete', args=[habit.id]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_other_user_cannot_get_archive_confirm_page(second_client_logged_in, habit):
    response = second_client_logged_in.get(reverse('habit-archive', args=[habit.id]))
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# 3. current_streak — longer broken streaks
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_current_streak_longer_gap(habit):
    with freeze_time("2026-06-30"):
        today = timezone.now().date()
        HabitLog.objects.create(habit=habit, date=today)
        # skip 3 days, then log further back — should not count toward current streak
        HabitLog.objects.create(habit=habit, date=today - timezone.timedelta(days=4))
        HabitLog.objects.create(habit=habit, date=today - timezone.timedelta(days=5))
        assert habit.current_streak() == 1


@pytest.mark.django_db
def test_current_streak_picks_streak_ending_today_not_a_past_one(habit):
    with freeze_time("2026-06-30"):
        today = timezone.now().date()
        # a long streak two weeks ago that is NOT connected to today
        for i in range(14, 19):
            HabitLog.objects.create(habit=habit, date=today - timezone.timedelta(days=i))
        # today's streak is only 2 days
        HabitLog.objects.create(habit=habit, date=today)
        HabitLog.objects.create(habit=habit, date=today - timezone.timedelta(days=1))
        assert habit.current_streak() == 2


# ---------------------------------------------------------------------------
# 4. longest_streak — multiple separate streaks, past streak longer than current
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_longest_streak_past_streak_longer_than_current(habit):
    with freeze_time("2026-06-30"):
        today = timezone.now().date()
        # a 5-day streak two weeks ago
        for i in range(14, 19):
            HabitLog.objects.create(habit=habit, date=today - timezone.timedelta(days=i))
        # a 2-day streak right now
        HabitLog.objects.create(habit=habit, date=today)
        HabitLog.objects.create(habit=habit, date=today - timezone.timedelta(days=1))
        assert habit.longest_streak() == 5


@pytest.mark.django_db
def test_longest_streak_multiple_equal_streaks(habit):
    with freeze_time("2026-06-30"):
        today = timezone.now().date()
        # two separate 2-day streaks, gap between them
        HabitLog.objects.create(habit=habit, date=today)
        HabitLog.objects.create(habit=habit, date=today - timezone.timedelta(days=1))
        HabitLog.objects.create(habit=habit, date=today - timezone.timedelta(days=5))
        HabitLog.objects.create(habit=habit, date=today - timezone.timedelta(days=6))
        assert habit.longest_streak() == 2


# ---------------------------------------------------------------------------
# 5. unique_together (user, name, frequency) — IntegrityError -> friendly form error
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_model_level_duplicate_habit_raises_integrity_error(habit, user):
    with pytest.raises(IntegrityError):
        Habit.objects.create(
            user=user, name=habit.name, frequency=habit.frequency, times_per_week=1,
        )


@pytest.mark.django_db
def test_create_duplicate_habit_via_view_shows_friendly_error(client_logged_in, habit):
    response = client_logged_in.post(reverse('habit-create'), {
        'name': habit.name,
        'frequency': habit.frequency,
        'times_per_week': 9,
    })
    # should re-render the form with an error, not 500 or redirect
    assert response.status_code == 200
    assert Habit.objects.filter(name=habit.name, frequency=habit.frequency).count() == 1
    assert response.context['form'].errors


@pytest.mark.django_db
def test_edit_habit_into_duplicate_shows_friendly_error(client_logged_in, habit, user):
    other = Habit.objects.create(
        user=user, name="Reading", frequency="daily", times_per_week=2,
    )
    response = client_logged_in.post(reverse('habit-edit', args=[other.id]), {
        'name': habit.name,            # collide with the `habit` fixture's name
        'frequency': habit.frequency,  # and frequency
        'times_per_week': 4,
    })
    assert response.status_code == 200
    other.refresh_from_db()
    assert other.name == "Reading"  # unchanged
    assert response.context['form'].errors


@pytest.mark.django_db
def test_create_same_name_different_frequency_is_allowed(client_logged_in, habit):
    # same name + different frequency should NOT collide (per unique_together)
    response = client_logged_in.post(reverse('habit-create'), {
        'name': habit.name,
        'frequency': 'weekly',
        'times_per_week': 1,
    })
    assert response.status_code == 302
    assert Habit.objects.filter(name=habit.name, frequency='weekly').exists()


# ---------------------------------------------------------------------------
# 6. HabitForm validation beyond "missing name"
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_form_valid_with_blank_optional_fields(user):
    form = HabitForm(data={
        'name': 'Stretching',
        'frequency': 'daily',
        'times_per_week': 1,
        'category': '',
        'color': '',
        'icon': '',
    })
    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_form_invalid_with_negative_times_per_week():
    form = HabitForm(data={
        'name': 'Running',
        'frequency': 'times_per_week',
        'times_per_week': -3,
    })
    # PositiveIntegerField should reject negative values
    assert not form.is_valid()
    assert 'times_per_week' in form.errors


@pytest.mark.django_db
def test_form_invalid_with_bad_frequency_choice():
    form = HabitForm(data={
        'name': 'Running',
        'frequency': 'sometimes',  # not a valid FrequencyChoices value
        'times_per_week': 3,
    })
    assert not form.is_valid()
    assert 'frequency' in form.errors


@pytest.mark.django_db
def test_create_habit_with_negative_times_per_week_does_not_save(client_logged_in):
    response = client_logged_in.post(reverse('habit-create'), {
        'name': 'Running',
        'frequency': 'times_per_week',
        'times_per_week': -3,
    })
    assert response.status_code == 200
    assert not Habit.objects.filter(name='Running').exists()


# ---------------------------------------------------------------------------
# 7. reorder_habits — non-POST request
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_reorder_habits_get_not_allowed(client_logged_in):
    response = client_logged_in.get(reverse('habit-reorder'))
    assert response.status_code == 405


@pytest.mark.django_db
def test_reorder_habits_requires_login(client):
    response = client.post(reverse('habit-reorder'))
    assert response.status_code == 302
    assert "login" in response.url


# ---------------------------------------------------------------------------
# 8. HabitLog unique_together (habit, date) outside the toggle flow
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_habitlog_duplicate_same_day_raises_integrity_error(habit):
    today = timezone.now().date()
    HabitLog.objects.create(habit=habit, date=today)
    with pytest.raises(IntegrityError):
        HabitLog.objects.create(habit=habit, date=today)


@pytest.mark.django_db
def test_toggle_habit_does_not_create_duplicate_logs_same_day(client_logged_in, habit):
    # toggle on, then toggle on again rapidly should not double-create
    # (the view's delete-or-create logic should keep this consistent)
    client_logged_in.post(reverse('habit-toggle', args=[habit.id]))
    today = timezone.now().date()
    assert HabitLog.objects.filter(habit=habit, date=today).count() == 1

    client_logged_in.post(reverse('habit-toggle', args=[habit.id]))
    assert HabitLog.objects.filter(habit=habit, date=today).count() == 0
