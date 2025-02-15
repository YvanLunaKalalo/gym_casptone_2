from django.contrib import admin
from .models import Workout, UserProfile, UserProgress, WorkoutSession
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

    list_display = ('user', 'Sex', 'Age', 'Height', 'Weight', 'BMI', 'Fitness_Goal')
    search_fields = ('user__username', 'Sex', 'Fitness_Goal')
    
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

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'workout', 'progress', 'date', 'completion_percentage', 'session_number', 'routine_number', 'preferred_reps')
    search_fields = ('user__username', 'workout__Title', 'session_number')
    
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
    
@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_name', 'session_date', 'is_completed', 'workout_count')
    search_fields = ('user__username', 'session_name', 'workouts__Title')  # Search by username, session name, or workout title

    # Optional: Add a custom template for the change list view
    change_list_template = "admin/workout_session_change_list.html"  # Custom template for change list

    def workout_count(self, obj):
        # Display the number of workouts in the session
        return obj.workouts.count()
    workout_count.short_description = 'Number of Workouts'

    def changelist_view(self, request, extra_context=None):
        # Data for pie chart or other statistics
        session_data = WorkoutSession.objects.values('user__username').annotate(session_count=Count('id'))
        usernames = [data['user__username'] for data in session_data]
        session_counts = [data['session_count'] for data in session_data]

        context = {
            'usernames': usernames,
            'session_counts': session_counts,
        }
        return super().changelist_view(request, extra_context=context)