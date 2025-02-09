from django.shortcuts import render, redirect, get_object_or_404
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
        progress_workout = UserProgress.objects.filter(user=request.user, progress__lt=100).first()
        has_profile = UserProfile.objects.filter(user=request.user).exists()

    context = {
        'progress_workout': progress_workout,  # Pass this to the template
        'has_profile': has_profile  # Pass the profile flag to the template
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