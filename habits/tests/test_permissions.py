import pytest
from django.urls import reverse
from habits.models import HabitLog


@pytest.mark.django_db
def test_other_user_cannot_edit(second_client_logged_in, habit):
    response = second_client_logged_in.post(
        reverse('habit-edit', args=[habit.id]),
        {'name': 'Malicious Edit', 'frequency': 'daily', 'times_per_week': 1},
    )
    assert response.status_code == 404
    habit.refresh_from_db()
    assert habit.name != 'Malicious Edit'


@pytest.mark.django_db
def test_other_user_cannot_toggle(second_client_logged_in, habit):
    response = second_client_logged_in.post(reverse('habit-toggle', args=[habit.id]))
    assert response.status_code == 404
    assert HabitLog.objects.filter(habit=habit).count() == 0


@pytest.mark.django_db
def test_other_user_cannot_delete(second_client_logged_in, habit):
    response = second_client_logged_in.post(reverse('habit-delete', args=[habit.id]))
    assert response.status_code == 404
    habit.refresh_from_db()  


@pytest.mark.django_db
def test_other_user_cannot_view_detail(second_client_logged_in, habit):
    response = second_client_logged_in.get(reverse('habit-detail', args=[habit.id]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_other_user_cannot_archive(second_client_logged_in, habit):
    response = second_client_logged_in.post(reverse('habit-archive', args=[habit.id]))
    assert response.status_code == 404
    habit.refresh_from_db()
    assert habit.is_active


@pytest.mark.django_db
def test_other_user_cannot_restore(second_client_logged_in, habit):
    habit.is_active = False
    habit.save()
    response = second_client_logged_in.post(reverse('habit-restore', args=[habit.id]))
    assert response.status_code == 404
    habit.refresh_from_db()
    assert not habit.is_active


@pytest.mark.django_db
def test_anonymous_redirect_habit_list(client):
    response = client.get(reverse('habit-list'))
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_anonymous_redirect_habit_detail(client, habit):
    response = client.get(reverse('habit-detail', args=[habit.id]))
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_anonymous_cannot_toggle(client, habit):
    response = client.post(reverse('habit-toggle', args=[habit.id]))
    assert response.status_code == 302
    assert "login" in response.url