from django.urls import path
from . import views

urlpatterns = [
    path('', views.habits, name='habit-list'),
    path('create/', views.create_habit, name='habit-create'),
    path('<int:habit_id>/edit/', views.edit_habit, name='habit-edit'),
    path('<int:habit_id>/delete/', views.delete_habit, name='habit-delete'),
    path('<int:habit_id>/toggle/', views.toggle_habit, name='habit-toggle'),
    path('<int:habit_id>/', views.habit_detail, name='habit-detail'),
    path('reorder/', views.reorder_habits, name='habit-reorder'),
    path('<int:habit_id>/archive/', views.archive_habit, name='habit-archive'),
    path('<int:habit_id>/restore/', views.restore_habit, name='habit-restore'),
    path('archived/', views.archived_habits, name='archived-habits'),
]
