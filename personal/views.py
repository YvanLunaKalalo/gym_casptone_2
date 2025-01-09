from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from personal.models import Contact
from machine_learning.models import Workout, UserProfile, UserProgress
from machine_learning.views import recommend_new_workouts  # Import function here

def index_view(request):
    template = loader.get_template('index.html')

    # Default values
    progress_workout = None
    has_profile = False  # Flag for checking if user has a profile
    completed_workouts = False  # Flag for checking if user has completed all workout
    show_recommendation_button = False  # Flag to determine if the button should be visible

    # Check if the user is authenticated
    if request.user.is_authenticated:
        progress_workout = UserProgress.objects.filter(user=request.user, completed=False).first()
        has_profile = UserProfile.objects.filter(user=request.user).exists()
        
        # Check if the user has completed all workouts
        completed_workouts = not UserProgress.objects.filter(user=request.user, completed=False).exists()
        
        # Set flag to show recommendation button if both workout and profile exist
        if has_profile and progress_workout:
            show_recommendation_button = True
            
        # When all workouts are completed, recommend new workouts
        if completed_workouts:
            try:
                user_profile = UserProfile.objects.get(user=request.user)
                recommend_new_workouts(request.user, user_profile)
            except UserProfile.DoesNotExist:
                user_profile = None  # In case the user doesn't have a profile yet

    context = {
        'progress_workout': progress_workout,  # Pass this to the template
        'has_profile': has_profile,  # Pass the profile flag to the template
        'completed_workouts': completed_workouts,  # Flag to indicate if workouts are completed
    }

    # Handle contact form submission
    if request.method == "POST":
        contact = Contact()
        contact.name = request.POST.get('name')
        contact.email = request.POST.get('email')
        contact.subject = request.POST.get('subject')
        contact.message = request.POST.get('message')
        contact.save()
        return render(request, "contact_done.html")
    
    return HttpResponse(template.render(context, request))

def recommend_new_workouts_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Get the user's profile
    user_profile = UserProfile.objects.get(user=request.user)

    # Call the function to recommend new workouts for the user
    recommend_new_workouts(request.user, user_profile)

    # Redirect the user to a page where they can view the recommended workouts
    return redirect('workout_session')  # Or another page where new workouts are shown

def workout_recommendations_view(request):
    # Logic for recommending workouts goes here
    recommendations = recommend_new_workouts()  # Replace with your logic

    context = {
        'recommendations': recommendations,
    }

    return render(request, "workout_recommendations.html", context)

def dashboard_view(request):
    # Check if the logged-in user has a profile
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None

    # Fetch all workout progress for the logged-in user
    user_progress = UserProgress.objects.filter(user=request.user).order_by('progress_date')

    # Calculate total workouts, completed workouts, and the progress percentage
    total_workouts = user_progress.count()
    completed_workouts = user_progress.filter(completed=True).count()
    progress_percentage = (completed_workouts / total_workouts) * 100 if total_workouts > 0 else 0
    
    # Prepare data for the line chart
    progress_dates = [progress.progress_date.strftime('%Y-%m-%d') for progress in user_progress]
    progress_values = [progress.progress for progress in user_progress]

    # Create context for the dashboard
    context = {
        'user_profile': user_profile,  # User profile data
        'user_progress': user_progress,  # All workout progress entries
        'total_workouts': total_workouts,
        'completed_workouts': completed_workouts,
        'progress_percentage': progress_percentage,
        'progress_dates': progress_dates,
        'progress_values': progress_values,
    }

    return render(request, 'dashboard.html', context)