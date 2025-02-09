from django.urls import path
from . import views

urlpatterns = [
    path('recommend/', views.workout_recommendation_view, name="recommend"),
    path('workout-session/', views.workout_session_view, name='workout_session'),
    path('generate-random-workouts/', views.generate_random_workouts, name='generate_random_workouts'),
    path('done-workout/', views.done_workout_view, name='done_workout'),
    path('not-done-workout/', views.not_done_workout_view, name='not_done_workout'),
    path('workout-complete/', views.workout_complete_view, name='workout_complete'),
    path('workout-progress/', views.workout_progress_view, name='workout_progress'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]