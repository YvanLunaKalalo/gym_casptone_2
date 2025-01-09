from django.db import models
from django.conf import settings

class Workout(models.Model):
    Title = models.CharField(max_length=255)
    Desc = models.TextField()
    Type = models.CharField(max_length=50, default='None')
    BodyPart = models.CharField(max_length=50)
    Equipment = models.CharField(max_length=50, default='None')
    Level = models.CharField(max_length=50, default='None')

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
    
class UserWorkoutSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    current_workout = models.ForeignKey(Workout, on_delete=models.SET_NULL, null=True, blank=True)
    completed = models.BooleanField(default=False)
    progress = models.PositiveIntegerField(default=0)  # Percentage completed

    def __str__(self):
        return f'{self.user.username} - Progress: {self.progress}%'    
    
    class Meta:
        verbose_name_plural = "Workout Sessions"
    
class UserProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    progress = models.IntegerField(default=0)  # Progress in percentage
    date = models.DateField(auto_now_add=True)
    progress_date = models.DateField(null=True, blank=True)  # Track when workout was completed
    completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.workout.Title} - Completed: {self.progress}"
    
    class Meta:
        verbose_name = "List of User Progress"  # Singular name in admin
        verbose_name_plural = "User Progress"  # Plural name in admin