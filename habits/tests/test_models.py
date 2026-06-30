import pytest
from freezegun import freeze_time
from django.utils import timezone
from habits.models import Habit, HabitLog


# CRITICAL FIX: freeze_time must wrap fixture creation too, not just the
# assertion. Fixtures (log_today, log_yesterday) call timezone.now() at
# fixture-resolution time, which happens BEFORE your test body runs. If you
# only freeze inside the test body, the logs get created with the REAL
# current date while your assertions think "today" is some frozen date.
# That mismatch is exactly what makes these tests non-deterministic.
#
# Fix: don't depend on the log_today/log_yesterday fixtures for these tests.
# Freeze time first, then create the logs manually inside the frozen block.

@pytest.mark.django_db
def test_get_log_dates(habit):
    with freeze_time("2026-06-30"):
        HabitLog.objects.create(habit=habit, date=timezone.now().date())
        log_dates = habit.get_log_dates()
        assert len(log_dates) == 1
        assert log_dates[0] == timezone.now().date()


@pytest.mark.django_db
def test_current_streak_single_log(habit):
    with freeze_time("2026-06-30"):
        HabitLog.objects.create(habit=habit, date=timezone.now().date())
        assert habit.current_streak() == 1


@pytest.mark.django_db
def test_current_streak_gap(habit):
    with freeze_time("2026-06-30"):
        HabitLog.objects.create(habit=habit, date=timezone.now().date())
        # gap: skip yesterday, log 2 days ago instead
        two_days_ago = timezone.now().date() - timezone.timedelta(days=2)
        HabitLog.objects.create(habit=habit, date=two_days_ago)
        # streak should be 1 (today only) because yesterday is missing
        assert habit.current_streak() == 1


@pytest.mark.django_db
def test_current_streak_zero_logs(habit):
    with freeze_time("2026-06-30"):
        assert habit.current_streak() == 0


@pytest.mark.django_db
def test_longest_streak_multiple(habit):
    with freeze_time("2026-06-30"):
        today = timezone.now().date()
        HabitLog.objects.create(habit=habit, date=today)
        HabitLog.objects.create(habit=habit, date=today - timezone.timedelta(days=1))
        HabitLog.objects.create(habit=habit, date=today - timezone.timedelta(days=2))
        assert habit.longest_streak() == 3


@pytest.mark.django_db
def test_longest_streak_zero_logs(habit):
    with freeze_time("2026-06-30"):
        assert habit.longest_streak() == 0


@pytest.mark.django_db
def test_total_completions(habit):
    with freeze_time("2026-06-30"):
        today = timezone.now().date()
        HabitLog.objects.create(habit=habit, date=today)
        HabitLog.objects.create(habit=habit, date=today - timezone.timedelta(days=1))
        assert habit.total_completions() == 2


@pytest.mark.django_db
def test_total_completions_zero(habit):
    assert habit.total_completions() == 0


@pytest.mark.django_db
def test_success_rate_capped_at_100(habit):
    # NOTE: confirm your success_rate() actual cap-triggering scenario —
    # this assumes logging every day for 7 days hits/exceeds 100%.
    with freeze_time("2026-06-30"):
        today = timezone.now().date()
        for i in range(7):
            HabitLog.objects.create(habit=habit, date=today - timezone.timedelta(days=i))
        assert habit.success_rate() <= 100.0
        assert habit.success_rate() == 100.0


@pytest.mark.django_db
def test_success_rate_zero_logs(habit):
    with freeze_time("2026-06-30"):
        assert habit.success_rate() == 0.0


@pytest.mark.django_db
def test_best_day_of_week(habit):
    with freeze_time("2026-06-30"):  # 2026-06-30 is a Tuesday
        monday = timezone.now().date() - timezone.timedelta(days=timezone.now().weekday())
        # log Monday three times across different weeks to make it the clear best day
        HabitLog.objects.create(habit=habit, date=monday)
        HabitLog.objects.create(habit=habit, date=monday - timezone.timedelta(days=7))
        HabitLog.objects.create(habit=habit, date=monday - timezone.timedelta(days=14))
        assert habit.best_day_of_week() == "Monday"


@pytest.mark.django_db
def test_best_day_of_week_no_logs(habit):
    with freeze_time("2026-06-30"):
        result = habit.best_day_of_week()
        # CONFIRM: what does your actual implementation return with no logs?
        # None? "" ? Adjust this assertion to match real behavior — don't
        # guess and lock in a wrong expectation.
        assert result is None or result == ""


@pytest.mark.django_db
def test_habitlog_creation_with_note(habit):
    log = HabitLog.objects.create(habit=habit, date=timezone.now().date(), note="test note")
    assert log.note == "test note"


@pytest.mark.django_db
def test_habitlog_creation_without_note(habit):
    log = HabitLog.objects.create(habit=habit, date=timezone.now().date())
    assert log.note in (None, "")


@pytest.mark.django_db
def test_habitlog_cascade_delete(habit):
    HabitLog.objects.create(habit=habit, date=timezone.now().date())
    assert HabitLog.objects.filter(habit=habit).count() == 1
    habit.delete()
    assert HabitLog.objects.filter(habit_id=habit.id).count() == 0