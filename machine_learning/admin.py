from django.contrib import admin
from .models import Workout, UserProfile, UserWorkoutSession, UserProgress
from django.db.models import Count
from django.shortcuts import render

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('Title', 'Desc', 'Type', 'BodyPart', 'Equipment', 'Level')
    search_fields = ('Title', 'Desc', 'Type', 'BodyPart', 'Equipment', 'Level')
    
    change_list_template = "admin/workout_change_list.html"  # Custom template for change list

    def changelist_view(self, request, extra_context=None):
        # Data for pie chart specific to workouts
        workout_data = Workout.objects.all().annotate(total_workouts=Count('id'))
        workout_titles = [workout.Title for workout in workout_data]
        workout_counts = [1] * len(workout_titles)  # Each workout counts as 1

        context = {
            'workout_titles': workout_titles,
            'workout_counts': workout_counts,
        }
        return super().changelist_view(request, extra_context=context)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = ('user', 'Sex', 'Age', 'Height', 'Weight', 'BMI', 'Fitness_Goal', 'Fitness_Type')
    search_fields = ('user__username', 'Sex', 'Fitness_Goal', 'Fitness_Type')
    
    change_list_template = "admin/userprofile_change_list.html"  # Custom template for change list

    def changelist_view(self, request, extra_context=None):
        # Data for pie chart specific to user profiles
        user_data = UserProfile.objects.all().annotate(total_profiles=Count('id'))
        fitness_goals = UserProfile.objects.values('Fitness_Goal').annotate(count=Count('Fitness_Goal'))
        fitness_goal_labels = [goal['Fitness_Goal'] for goal in fitness_goals]
        fitness_goal_counts = [goal['count'] for goal in fitness_goals]

        context = {
            'fitness_goal_labels': fitness_goal_labels,
            'fitness_goal_counts': fitness_goal_counts,
        }
        return super().changelist_view(request, extra_context=context)

@admin.register(UserWorkoutSession)
class UserWorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_workout', 'progress', 'completed')
    search_fields = ('user__username', 'current_workout__Title')
    list_filter = ('completed',)  # Filter based on completed status

    def changelist_view(self, request, extra_context=None):
        # Data for pie chart specific to workout session progress
        session_data = UserWorkoutSession.objects.values('current_workout__Title').annotate(total_sessions=Count('id'))
        workout_titles = [data['current_workout__Title'] for data in session_data]
        session_counts = [data['total_sessions'] for data in session_data]

        extra_context = extra_context or {}
        extra_context['workout_titles'] = workout_titles
        extra_context['session_counts'] = session_counts

        return super().changelist_view(request, extra_context=extra_context)

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'workout', 'progress', 'date', 'progress_date', 'completed')
    search_fields = ('user__username', 'workout__Title')
    
    change_list_template = "admin/userprogress_change_list.html"  # Custom template for change list

    def changelist_view(self, request, extra_context=None):
        # Data for pie chart specific to user progress
        progress_data = UserProgress.objects.values('workout__Title').annotate(total_progress=Count('id'))
        workout_titles = [data['workout__Title'] for data in progress_data]
        progress_counts = [data['total_progress'] for data in progress_data]

        context = {
            'workout_titles': workout_titles,
            'progress_counts': progress_counts,
        }
        return super().changelist_view(request, extra_context=context)