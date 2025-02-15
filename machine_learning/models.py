from django.db import models
from django.conf import settings

class Workout(models.Model):
    Title = models.CharField(max_length=255)
    Desc = models.TextField()
    Type = models.CharField(max_length=50, default='None')
    BodyPart = models.CharField(max_length=50)
    Equipment = models.CharField(max_length=50, default='None')
    Level = models.CharField(max_length=50, default='None')
    Repetitions = models.IntegerField(default=0)

    def __str__(self):
        return self.Title
    
    class Meta:
        verbose_name = "List of Workouts"  # Singular name in admin
        verbose_name_plural = "Workouts"  # Plural name in admin

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    Sex = models.CharField(max_length=10)
    Age = models.PositiveIntegerField()
    Height = models.FloatField()
    Weight = models.FloatField()
    Hypertension = models.CharField(max_length=10, default='No')
    Diabetes = models.CharField(max_length=10, default='No')
    BMI = models.FloatField()
    Level = models.CharField(max_length=50, default='Normal')
    Fitness_Goal = models.CharField(max_length=50, default='Weight_Loss')
    Fitness_Type = models.CharField(max_length=50, default='Cardio_Fitness')

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name = "List of User Profiles"  # Singular name in admin
        verbose_name_plural = "User Profiles"  # Plural name in admin
    
class UserProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    progress = models.IntegerField(default=0)  # Progress in percentage
    date = models.DateField(auto_now_add=True)
    repetitions = models.IntegerField(default=0)
    completion_percentage = models.FloatField(default=0.0)  # Store completion percentage for the workout
    session_number = models.IntegerField(default=1)  # Store the session number or week number
    routine_number = models.IntegerField(default=1)  # Add this field
    week_number = models.IntegerField(default=1)  # Add this field
    preferred_reps = models.IntegerField(default=0)  # New field to store preferred repetitions

    def __str__(self):
        return f"{self.user.username} - {self.workout.Title} - Completed: {self.completion_percentage} - Week {self.session_number}"
    
    class Meta:
        verbose_name = "List of User Progress"  # Singular name in admin
        verbose_name_plural = "User Progress"  # Plural name in admin
        
class WorkoutSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session_name = models.CharField(max_length=255, blank=True, null=True)  # Name of the session (optional)
    workouts = models.ManyToManyField(Workout)
    session_date = models.DateField(auto_now_add=True)
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    incomplete_workouts = models.TextField(blank=True)  # Store incomplete workouts in this field
    total_repetitions_completed = models.IntegerField(default=0)  # Total reps done for the session
    is_completed = models.BooleanField(default=False)  # Flag to mark if the session is completed
    session_number = models.PositiveIntegerField(default=0)  # Track the session number

    def __str__(self):
        return f"Session {self.id} for {self.user.username}"