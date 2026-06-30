import pytest
from django.urls import reverse
from habits.models import Habit


@pytest.mark.django_db
def test_habit_list(client_logged_in, habit):
    response = client_logged_in.get(reverse('habit-list'))
    assert response.status_code == 200
    assert habit.name in [h.name for h in response.context['habits']]


@pytest.mark.django_db
def test_create_habit(client_logged_in, user):
    response = client_logged_in.post(reverse('habit-create'), {
        'name': 'Meditation',
        'frequency': 'daily',
        'times_per_week': 5,
    })
    assert response.status_code == 302
    new_habit = Habit.objects.get(name='Meditation')
    assert new_habit.user == user


@pytest.mark.django_db
def test_create_habit_invalid_missing_name(client_logged_in):
    response = client_logged_in.post(reverse('habit-create'), {
        'frequency': 'daily',
        'times_per_week': 5,
    })
    # CONFIRM: does your form re-render with 200 + errors, or something else?
    assert response.status_code == 200
    assert not Habit.objects.filter(frequency='daily', times_per_week=5).exists()


@pytest.mark.django_db
def test_edit_habit(client_logged_in, habit):
    response = client_logged_in.post(reverse('habit-edit', args=[habit.id]), {
        'name': 'Updated Habit',
        'frequency': 'daily',
        'times_per_week': 4,
    })
    assert response.status_code == 302
    habit.refresh_from_db()
    assert habit.name == 'Updated Habit'
    assert habit.times_per_week == 4


@pytest.mark.django_db
def test_delete_habit(client_logged_in, habit):
    response = client_logged_in.post(reverse('habit-delete', args=[habit.id]))
    assert response.status_code == 302
    with pytest.raises(Habit.DoesNotExist):
        Habit.objects.get(id=habit.id)


@pytest.mark.django_db
def test_habit_detail(client_logged_in, habit):
    response = client_logged_in.get(reverse('habit-detail', args=[habit.id]))
    assert response.status_code == 200
    assert response.context['habit'].id == habit.id
    assert habit.name in response.content.decode()


@pytest.mark.django_db
def test_habit_list_excludes_other_users_habits(client_logged_in, habit, second_user_habit):
    response = client_logged_in.get(reverse('habit-list'))
    names = [h.name for h in response.context['habits']]
    assert habit.name in names
    assert second_user_habit.name not in names


@pytest.mark.django_db
def test_habit_list_excludes_archived(client_logged_in, habit):
    habit.is_active = False
    habit.save()
    response = client_logged_in.get(reverse('habit-list'))
    names = [h.name for h in response.context['habits']]
    assert habit.name not in names