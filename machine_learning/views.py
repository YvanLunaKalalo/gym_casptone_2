from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from joblib import load
import pandas as pd
from django.conf import settings
from sklearn.metrics.pairwise import cosine_similarity
from .models import Workout, UserProfile, UserProgress, WorkoutSession
from django.utils.timezone import now
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages
import random

# Load the pre-trained model
vectorizer = load('./Saved_Models/vectorizer.pkl') # Recommended Workout 2

# Load workout data (you might need to adjust the file path)
workout_data = pd.read_csv(settings.NOTEBOOKS_DIR / 'Datasets' / 'archive(2)' / 'megaGymDataset.csv')

# Combine relevant features from workout_data
workout_data['combined_features'] = workout_data['Title'] + " " + workout_data['Desc']
workout_data['combined_features'] = workout_data['combined_features'].fillna('')

# Transform workout features using the vectorizer
workout_features_matrix = vectorizer.transform(workout_data['combined_features'])

def get_repetitions(Fitness_goal):
    """
    Determines the repetitions based on the user's fitness goal.
    """
    if Fitness_goal == 'Weight Gain':
        return 12  # Lower reps for muscle gain (focus on heavier weights)
    elif Fitness_goal == 'Weight Loss':
        return 15  # Higher reps for weight loss (moderate weights)
    else:
        return 0  # Default reps if no goal is provided

# Define the view for workout recommendations
def workout_recommendation_view(request):
    template = loader.get_template("profile_form.html")  # Your form template
    
    if not request.user.is_authenticated:
        return redirect("login")

    context = {}        

    if request.method == 'POST':
        # Get profile data from form submission
        # Use .get() to safely retrieve POST data
        Sex = request.POST.get('Sex', '')  # Default value is an empty string if 'Sex' is missing
        Age = request.POST.get('Age', '')
        Height = request.POST.get('Height', '')
        Weight = request.POST.get('Weight', '')
        Hypertension = request.POST.get('Hypertension', '')
        Diabetes = request.POST.get('Diabetes', '')
        Level = request.POST.get('Level', '')
        Fitness_Goal = request.POST.get('Fitness Goal', '')
        Fitness_Type = request.POST.get('Fitness Type', '')
        
        # Calculate BMI (BMI = weight in kg / (height in meters)^2)
        try:
            height_in_centimeters = float(Height) / 100  # Convert height from cm to meters
            weight_in_kg = float(Weight)  # Convert weight to kg
            BMI = weight_in_kg / (height_in_centimeters ** 2)
            BMI = round(BMI, 2)  # Round to two decimal places
        except (ValueError, ZeroDivisionError):
            # If there's an invalid input for height or weight, set BMI to None
            BMI = None

        # Save profile data in the database
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'Sex': Sex, 'Age': Age, 'Height': Height, 'Weight': Weight,
                'Hypertension': Hypertension, 'Diabetes': Diabetes, 'BMI': BMI,
                'Level': Level, 'Fitness_Goal': Fitness_Goal, 'Fitness_Type': Fitness_Type
            }
        )
        
        # Get current session number (e.g., based on the current date or week number)
        current_week_number = timezone.now().isocalendar()[1]  # Week number of the year

        columns = ['Age', 'Height', 'Weight', 'BMI', 'Sex_Female', 'Sex_Male', 'Hypertension_No', 'Hypertension_Yes', 'Diabetes_No', 'Diabetes_Yes', 'Level_Normal', 'Level_Obuse', 'Level_Overweight', 'Level_Underweight', 'Fitness Goal_Weight Gain', 'Fitness Goal_Weight Loss', 'Fitness Type_Cardio Fitness', 'Fitness Type_Muscular Fitness']
        data = {
            'Age': [Age],
            'Height': [Height],
            'Weight' : [Weight],
            'BMI' : [BMI],
            'Sex_Female': [1 if Sex == 'Female' else 0],
            'Sex_Male': [1 if Sex == 'Male' else 0],
            'Hypertension_No' : [1 if Hypertension == 'No' else 0],
            'Hypertension_Yes' : [1 if Hypertension == 'Yes' else 0],
            'Diabetes_No' : [1 if Diabetes == 'No' else 0],
            'Diabetes_Yes' : [1 if Diabetes == 'Yes' else 0],
            'Level_Normal' : [1 if Level == 'Normal' else 0],
            'Level_Obuse' : [1 if Level == 'Obese' else 0],
            'Level_Overweight' : [1 if Level == 'Overweight' else 0],
            'Level_Underweight' : [1 if Level == 'Underweight' else 0],
            'Fitness Goal_Weight Gain' : [1 if Fitness_Goal == 'Weight Gain' else 0],
            'Fitness Goal_Weight Loss' : [1 if Fitness_Goal == 'Weight Loss' else 0],
            'Fitness Type_Cardio Fitness' : [1 if Fitness_Type == 'Cardio Fitness' else 0],
            'Fitness Type_Muscular Fitness' : [1 if Fitness_Type == 'Muscular Fitness' else 0],
        }
        
        # Calculate repetitions based on fitness goal
        repetitions = get_repetitions(Fitness_Goal)

        # In this case, we'll just use the `Level`, `Fitness_Goal`, and `Fitness_Type` (categorical data) as a proxy
        profile_vector = vectorizer.transform([f"{Sex} {Age} {Height} {Weight} {Hypertension} {Diabetes} {BMI} {Level} {Fitness_Goal} {Fitness_Type}"])

        # Compute cosine similarity between profile and workout data
        similarity_scores = cosine_similarity(profile_vector, workout_features_matrix)
        print(similarity_scores)

        # Get top 5 recommended workouts
        top_indices = similarity_scores[0].argsort()[-15:][::-1]
        recommended_workouts = workout_data.iloc[top_indices]
        
        # Create a workout plan (7 days with 5 workouts per day)
        workout_plan = {}
        for day in range(1, 4):  # 7 days of the week
            workout_plan[day] = recommended_workouts.iloc[(day-1)*5: day*5][['Title', 'Desc', 'Type', 'BodyPart', 'Equipment', 'Level']].to_dict(orient='records')
            
        # Save recommended workouts to the UserProgress model
        for _, workout in recommended_workouts.iterrows():
            workout_instance, created = Workout.objects.get_or_create(
                Title=workout['Title'],
                defaults={
                    'Desc': workout['Desc'],
                    'Type': workout['Type'],
                    'BodyPart': workout['BodyPart'],
                    'Equipment': workout.get('Equipment', 'None'),
                    'Level': workout.get('Level', 'None'),
                }
            )

            # Create a UserProgress entry for each recommended workout
            UserProgress.objects.get_or_create(
                user=request.user,
                workout=workout_instance,
                session_number=current_week_number,  # Use the session number or week number
                defaults={'progress': 0}  # Initialize progress to 0
            )
            
        # Pass recommended workouts to the template
        context = {
            "recommended_workouts" : recommended_workouts[['Title', 'Desc', 'Type', 'BodyPart', 'Equipment', 'Level']].to_dict(orient='records'),
            "repetitions": repetitions,  # Pass repetitions to the template if needed
            "workout_plan" : workout_plan,
        }
        
        return render(request, 'workout_recommendations.html', context)  # Render the output template

    return HttpResponse(template.render(context, request))

# Define the view for workout sessions
def workout_session_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    # Get the selected routine number from the query parameters
    routine_number = request.GET.get('routine', 1)
    routine_number = int(routine_number)

    # Get the user's workout progress
    workout_progress = UserProgress.objects.filter(user=request.user)
    user_profile = get_object_or_404(UserProfile, user=request.user) # Get the user's profile to access fitness goal and determine repetitions
    repetitions_per_workout = get_repetitions(user_profile.Fitness_Goal)
    preferred_reps = UserProgress.preferred_reps
        
    # current_workout_index = request.session.get('current_workout_index', 0) # Get the current workout index from the session or start at 0
    workouts_per_session = 5
    start_index = (routine_number - 1) * workouts_per_session
    total_workouts = workout_progress.count() # Organize the workout plan per day
    # session_number = request.session.get('session_number', 1)

    if start_index >= total_workouts:
        # All workouts are completed, save the session progress
        workout_session = UserProgress.objects.create(
            user=request.user,
            session_number=request.session.get('session_number', 1),
            completion_percentage=request.session.get('completion_percentage', 100)
        )
        workout_session.save()
        # workout_session, created = UserProgress.objects.get_or_create(
        #     user=request.user,
        #     session_number=request.session.get('session_number', 1),
        #     defaults={'completion_percentage': 100}
        # )
        
        # Increment the session number for the next session
        routine_number += 1
        request.session['routine_number'] = routine_number
        
        # Reset the session for a new routine
        request.session['start_index'] = 0
        request.session['new_session'] = True

        # After saving, redirect to a page indicating the routine is restarting
        return render(request, 'generate_random_workouts') # All workouts are completed

    # Get the current set of workouts (5 workouts at a time)
    end_index = min(start_index + workouts_per_session, total_workouts)
    current_workouts = workout_progress[start_index:end_index]
        
    # Initialize total repetitions completed for the current session (LAST CODE)
    if 'new_session' not in request.session or request.session['new_session']:
        request.session['total_repetitions_completed'] = 0  # Reset total reps for the new day/session
        request.session['new_session'] = False  # Mark session as started
    
    total_repetitions_completed = request.session.get('total_repetitions_completed', 0)  # Retrieve from session

    reps_exceed_limit = False  # Flag for reps exceeding limit
    total_repetitions_expected = repetitions_per_workout * workouts_per_session # Calculate the total repetitions expected for the day
    # session_number = request.session.get('session_number', 1) # Get or set the session number in the request session # Default to 1 if not set
        
    if request.method == 'POST':
        print("Form data submitted:", request.POST)  # Debugging form data
        
        reps_exceed_limit = False # Flag to track if any reps exceed the limit
        reps_incomplete = False  # Flag to check if reps are incomplete
        
        # Update workout progress for each workout in the current set
        for workout in current_workouts:
            reps_completed = request.POST.get(f'workout_{workout.id}_reps', 0)
            
            preferred_reps = request.POST.get(f'workout_{workout.id}_preferred_reps', 0)
            
            # Convert reps_completed to an integer
            reps_completed = int(reps_completed) if reps_completed else 0  # Handle empty field case
            
            preferred_reps = int(preferred_reps) if preferred_reps else 0  # Handle empty field case

            print(f"Reps completed for workout {workout.id}: {reps_completed}")
            print(f"Preferred reps for workout {workout.id}: {preferred_reps}")
            
            total_repetitions_completed += reps_completed # Add to the total completed repetitions
            
            # Check if reps completed exceeds the expected repetitions for the workout
            if reps_completed > preferred_reps:
                reps_exceed_limit = True
                messages.error(request, f"Some Reps exceeded the limit of {preferred_reps} reps.")
                break  # Stop the loop and do not update any workouts 
            
            # Check if the reps completed are less than the required reps
            if reps_completed <= preferred_reps:
                # reps_incomplete = True
            
                workout.progress = reps_completed  # Update the reps (progress)
                workout.preferred_reps = preferred_reps  # Update the preferred reps
                workout.save()
            
            # Update progress for the current workout (create a new record for each session)
            # new_workout_progress = UserProgress.objects.create(
            #     user=request.user,
            #     workout=workout.workout,
            #     progress=reps_completed,  # Store reps as progress
            #     preferred_reps=preferred_reps,
            #     routine_number=routine_number  # Record the session number
            # )
            # new_workout_progress.save()

            # If any reps are incomplete, prevent proceeding to the next workout plan
            # if reps_incomplete:
            #     completion_percentage = (total_repetitions_completed / total_repetitions_expected) * 100
            #     request.session['completion_percentage'] = round(completion_percentage, 2)
                
                # Move to the next day for the next submission
            # request.session['current_day'] = session_number + 1

            # If all days are completed, mark the workout as done
            # if session_number >= 3
            #     request.session['current_workout_index'] = end_index
            #     request.session['session_number'] = 1  # Reset to day 1 for the next session
            
            # total_repetitions_completed += reps_completed # Add to the total completed repetitions
            
            # Move to the next day for the next submission
            # request.session['session_number'] = session_number + 1

        if reps_exceed_limit:
            return redirect('workout_session')  # Redirect back to the workout session without updating the session variables
        
        # If all workouts are not completed, stay on the same plan
        # if not all_workouts_completed:
        #     return redirect('workout_session')  # Redirect back to the workout session without updating the session variables
            
        # After loop, print the total repetitions completed so far
        print(f"Total reps completed after POST: {total_repetitions_completed}")
                
        # Save the updated total reps in the session
        # request.session['total_repetitions_completed'] = total_repetitions_completed
        
        # If any workout is incomplete, do not move to the next plan
        # if has_incomplete_workouts:
            # messages.info(request, "You have unfinished workouts. Complete all repetitions to proceed.")
            # return redirect('done_workout')  # Redirect to the same session
            
        # If any reps are incomplete, prevent proceeding to the next workout plan
        if reps_incomplete:
            completion_percentage = (total_repetitions_completed / total_repetitions_expected) * 100
            request.session['completion_percentage'] = round(completion_percentage, 2)
            
            # messages.error(request, "You need to complete all repetitions before moving to the next workout plan.")
            return redirect('workout_progress')
        
        # Calculate and save completion percentage
        if total_repetitions_expected > 0:
            completion_percentage = (total_repetitions_completed / total_repetitions_expected) * 100
            request.session['completion_percentage'] = round(completion_percentage, 2)
        else:
            completion_percentage = 0

        # Save the workout progress into the database (WorkoutHistory)
        # workout_session = WorkoutSession.objects.create(
        #     user=request.user,
        #     session_number=session_number,
        #     completion_percentage=completion_percentage
        # )
            
        print(f"Completion percentage: {completion_percentage}%")
            
        # print(f"Total reps completed: {total_repetitions_completed}")
        # print(f"Total reps expected: {total_repetitions_expected}")
        # print(f"Completion percentage: {completion_percentage}%")
            
        # Reset session variables for the next workout session
        request.session['total_repetitions_completed'] = 0  # Reset total reps for the next session
        request.session['start_index'] = end_index  # Move to the next set of workouts
        
        # Increment the session number for the next set of workouts
        routine_number += 1
        request.session['routine_number'] = routine_number
        request.session['new_session'] = True  # Mark session as new for the next day (LAST CODE)
                
        # Reset session variables for the next workout session
        if end_index >= total_workouts:
            request.session['has_unfinished_workout'] = False
        else:
            request.session['has_unfinished_workout'] = True
                                    
        # Redirect to done_workout.html to show progress
        return redirect('workout_progress')
    
     # Set 'has_unfinished_workout' to True if there are still workouts to complete
    request.session['has_unfinished_workout'] = start_index < total_workouts
    
    # Calculate the percentage of repetitions completed
    if total_repetitions_expected > 0:
        completion_percentage = (total_repetitions_completed / total_repetitions_expected) * 100
        request.session['completion_percentage'] = round(completion_percentage, 2)
        
    else:
        completion_percentage = 0
        
    print(f"Total repetitions completed: {total_repetitions_completed}")
    print(f"Total repetitions expected: {total_repetitions_expected}")
    print(f"Completion percentage: {completion_percentage}%")

    context = {
        "current_workouts": current_workouts,
        "start_index": start_index + 1,  # Human-readable index
        "total_workouts": total_workouts,
        "end_workout_index": end_index,
        "completion_percentage": round(completion_percentage, 2),  # Round to two decimal places
        "progress_workout": start_index < total_workouts,  # If there are unfinished workouts
        "is_last_workout": end_index >= total_workouts,  # Check if it's the last workout
        # "session_number": session_number,
        "routine_number": routine_number
    }

    return render(request, 'workout_session.html', context)

def generate_random_workouts(request):
    if not request.user.is_authenticated:
        return redirect("login")

    user_profile = get_object_or_404(UserProfile, user=request.user)
    fitness_goal = user_profile.Fitness_Goal
    fitness_type = user_profile.Fitness_Type
    level = user_profile.Level

    # Get the latest session number (week number) for the user
    latest_progress = UserProgress.objects.filter(user=request.user).order_by('-session_number').first()
    if latest_progress:
        current_week_number = latest_progress.session_number + 1  # Increment week number
    else:
        current_week_number = 1  # Start with Week 1 if no progress exists

    # Filter workouts based on the user's profile
    filtered_workouts = Workout.objects.filter(
        Level=level,
        Type=fitness_type
    )

    # If no workouts match the criteria, fallback to all workouts
    if not filtered_workouts.exists():
        filtered_workouts = Workout.objects.all()

    # Randomly select 15 workouts (3 days x 5 workouts)
    random_workouts = random.sample(list(filtered_workouts), min(15, filtered_workouts.count()))

    # Split into 3 days
    workout_plan = {}
    for day in range(1, 4):  # 3 days
        workout_plan[day] = random_workouts[(day-1)*5: day*5]

    # Save the new workout plan to UserProgress with the incremented week number
    for day, workouts in workout_plan.items():
        for workout in workouts:
            UserProgress.objects.create(
                user=request.user,
                workout=workout,
                session_number=current_week_number,  # Use the incremented week number
                progress=0  # Initialize progress to 0
            )

    # Pass the new workout plan to the template
    context = {
        "workout_plan": workout_plan,
        "current_week_number": current_week_number,
    }

    return render(request, 'random_workouts.html', context)

def done_workout_view(request):
    # Get the completion percentage from the session (set in workout_session_view)
    completion_percentage = request.session.get('completion_percentage', 0)
    print(f"Completion percentage from session: {completion_percentage}")
    
    # Get the total number of workouts and the current workout index to check if it's the last workout
    total_workouts = UserProgress.objects.filter(user=request.user).count()
    current_workout_index = request.session.get('current_workout_index', 0)
    
    is_last_workout = current_workout_index >= total_workouts
    
    completion_percentage = min(completion_percentage, 100)  # Cap it at 100%

    context = {
        "completion_percentage": completion_percentage,
        "is_last_workout": is_last_workout
    }

    return render(request, 'done_workout.html', context)

def not_done_workout_view(request):
    # Get the completion percentage from the session (set in workout_session_view)
    completion_percentage = request.session.get('completion_percentage', 0)
    print(f"Completion percentage from session: {completion_percentage}")
    
    # Get the total number of workouts and the current workout index to check if it's the last workout
    total_workouts = UserProgress.objects.filter(user=request.user).count()
    current_workout_index = request.session.get('current_workout_index', 0)
    
    is_last_workout = current_workout_index >= total_workouts
    
    context = {
        "completion_percentage": completion_percentage,
        "is_last_workout": is_last_workout,
    }

    return render(request, 'not_done_workout.html', context)

def workout_complete_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    context = {}
    
    return render(request, 'workout_complete.html')

def workout_progress_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    # Get the user's workout progress and profile
    workout_progress = UserProgress.objects.filter(user=request.user)
    # print(workout_progress)  # Debugging: Check if workouts are being fetched

    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    total_workouts = workout_progress.count()

    # Store workout completion percentage per workout   
    workout_percentages = []
    total_reps_completed = 0
    total_reps_expected = 0
    
    # Group progress by session_number
    routine_data = {i: [] for i in range(1, 7)}  # For 6 days

    for workout in workout_progress:
        # Calculate reps completed for each workout
        reps_completed = workout.progress
        reps_expected = workout.preferred_reps # Assuming this gives the expected reps per workout
        total_reps_completed += reps_completed
        total_reps_expected += reps_expected

        # Calculate completion percentage for each workout
        completion_percentage = (reps_completed / reps_expected) * 100 if reps_expected else 0
        completion_percentage = min(completion_percentage, 100)  # Ensure it doesn't exceed 100
        workout_percentages.append({
            "workout": workout,
            "completion_percentage": round(completion_percentage, 2),
            "date": workout.date,  # Include the date in the workout data
            "routine_number": workout.routine_number,  # Capture the session number
        })
        
        # Group workouts by routine_number
        routine_data[workout.routine_number].append({
            "workout": workout,
            "completion_percentage": round(completion_percentage, 2),
            "date": workout.date,
        })

    # Calculate overall progress for the entire plan
    if total_reps_expected > 0:
        overall_progress = (total_reps_completed / total_reps_expected) * 100
        overall_progress = min(overall_progress, 100)  # Ensure it doesn't exceed 100

    else:
        overall_progress = 0
        
    # Split workouts into groups of 5 (workout plans)
    # workout_plans = [workout_percentages[i:i + 5] for i in range(0, len(workout_percentages), 5)]
    
    # Split workouts into groups of 5 (workout plans) and calculate average progress for each plan
    workout_plans = []
    for i in range(0, len(workout_percentages), 5):
        plan = workout_percentages[i:i + 5]
        plan_total = sum(workout['completion_percentage'] for workout in plan)
        average_completion = plan_total / len(plan) if len(plan) > 0 else 0
        workout_plans.append({
            "workouts": plan,
            "average_completion": round(average_completion, 2)
        })
        
    context = {
        "workout_percentages": workout_percentages,
        "overall_progress": round(overall_progress, 2),  # Round the overall progress
        "total_workouts": total_workouts,
        "workout_plans": workout_plans,  # Send the grouped workout plans to the template
        "routine_data": routine_data,  # Send the grouped routine data to the template
    }   

    return render(request, 'workout_progress.html', context)

def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    # Get the user's profile and progress
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    workout_progress = UserProgress.objects.filter(user=request.user)
    total_workouts = workout_progress.count()

    # Store workout completion percentage per workout
    workout_percentages = []
    total_reps_completed = 0
    total_reps_expected = 0
    
    # Group progress by session_number
    routine_data = {i: [] for i in range(1, 7)}  # For 6 days

    for workout in workout_progress:
        # Calculate reps completed for each workout
        reps_completed = workout.progress
        reps_expected = workout.preferred_reps # Assuming this gives the expected reps per workout
        total_reps_completed += reps_completed
        total_reps_expected += reps_expected

        # Calculate completion percentage for each workout
        completion_percentage = (reps_completed / reps_expected) * 100 if reps_expected else 0
        completion_percentage = min(completion_percentage, 100)  # Ensure it doesn't exceed 100
        workout_percentages.append({
            "workout": workout,
            "completion_percentage": round(completion_percentage, 2),
            "date": workout.date,  # Include the date in the workout data
            "routine_number": workout.routine_number  # Capture the session number
        })
        
        # Group workouts by routine_number
        routine_data[workout.routine_number].append({
            "workout": workout,
            "completion_percentage": round(completion_percentage, 2),
            "date": workout.date,
        })

    # Calculate overall progress for the entire plan
    if total_reps_expected > 0:
        overall_progress = (total_reps_completed / total_reps_expected) * 100
        overall_progress = min(overall_progress, 100)  # Ensure it doesn't exceed 100
    else:
        overall_progress = 0

    # Split workouts into groups of 5 (workout plans) and calculate average progress for each plan
    workout_plans = []
    for i in range(0, len(workout_percentages), 5):
        plan = workout_percentages[i:i + 5]
        plan_total = sum(workout['completion_percentage'] for workout in plan)
        average_completion = plan_total / len(plan) if len(plan) > 0 else 0
        workout_plans.append({
            "workouts": plan,
            "average_completion": round(average_completion, 2)
        })

    context = {
        "user_profile": user_profile,
        "total_workouts": total_workouts,
        "overall_progress": round(overall_progress, 2),  # Round the overall progress
        "workout_plans": workout_plans,  # Send the grouped workout plans to the template
        "routine_data": routine_data,  # Send the grouped routine data to the template
    }

    return render(request, 'dashboard.html', context)