from django.urls import path
from . import views

urlpatterns = [
    path('', views.habits, name='habits'),
    path('create/', views.create_habit, name='create_habit'),
    path('<int:habit_id>/edit/', views.edit_habit, name='edit_habit'),
    path('<int:habit_id>/delete/', views.delete_habit, name='delete_habit'),
    path('<int:habit_id>/toggle/', views.toggle_habit, name='toggle_habit'),
    path('<int:habit_id>/', views.habit_detail, name='habit_detail'),
    path('reorder/', views.reorder_habits, name='reorder_habits'),
    path('<int:habit_id>/archive/', views.archive_habit, name='archive_habit'),
    path('<int:habit_id>/restore/', views.restore_habit, name='restore_habit'),
    path('archived/', views.archived_habits, name='archived_habits'),
]
