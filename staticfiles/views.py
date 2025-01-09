from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from personal.models import Contact
from machine_learning.models import Workout, UserProfile, UserProgress

def index_view(request):
    template = loader.get_template('index.html')

    # Check if the user has an ongoing workout session
    progress_workout = None
    has_profile = False  # Flag for checking if user has a profile
    if request.user.is_authenticated:
        progress_workout = UserProgress.objects.filter(user=request.user, completed=False).first()
        has_profile = UserProfile.objects.filter(user=request.user).exists()


    context = {
        'progress_workout': progress_workout,  # Pass this to the template
        'has_profile': has_profile  # Pass the profile flag to the template
    } 
       
    if request.method=="POST":
        contact = Contact()
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        contact.name = name
        contact.email = email
        contact.subject = subject
        contact.message = message
        contact.save()
        return render(request, "contact_done.html")

    return HttpResponse(template.render(context, request))


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    # Get the user profile for the logged-in user
    user_profile = UserProfile.objects.filter(user=request.user).first()

    # Fetch all progress and workouts associated with the logged-in user
    user_progress = UserProgress.objects.filter(user=request.user)
    
    # Fetch all workouts
    all_workouts = Workout.objects.all()
    
    # Group workouts into days (e.g., each day contains 5 workouts)
    workouts_per_day = 5  # Adjust this number as needed
    days = []
    current_day = []
    for index, workout in enumerate(all_workouts, start=1):
        current_day.append(workout)
        if index % workouts_per_day == 0:
            days.append(current_day)
            current_day = []

    if current_day:
        days.append(current_day)  # Add remaining workouts to the last day
    
    # Calculate the progress per day
    days_progress = []
    for day_workouts in days:
        completed_count = 0
        for workout in day_workouts:
            progress = user_progress.filter(workout=workout).first()
            if progress and progress.completed:
                completed_count += 1
        # Calculate progress percentage for this day
        day_progress_percentage = (completed_count / len(day_workouts)) * 100
        days_progress.append({
            'day_workouts': day_workouts,
            'progress_percentage': day_progress_percentage
        })

    context = {
        'user_profile': user_profile,
        'days_progress': days_progress,  # List of days with workouts and progress
    }

    return render(request, 'dashboard.html', context)