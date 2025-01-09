from django.urls import path
from . import views

urlpatterns = [
    path('recommend/', views.workout_recommendation_view, name="recommend"),
    path('workout-session/', views.workout_session_view, name='workout_session'),
    path('workout-complete/', views.complete_workout_view, name='complete_workout'),
    path('workout-completed/', views.workout_complete_view, name='workout_complete'),
    path('progress-tracker/', views.progress_tracker_view, name='progress_tracker'),
    path('update-profile/', views.update_profile_view, name='update_profile'),
]