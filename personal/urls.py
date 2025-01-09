from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('workout-recommendations/', views.workout_recommendations_view, name='workout_recommendations'),
    path('recommend-new-workouts/', views.recommend_new_workouts_view, name='recommend_new_workouts'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]