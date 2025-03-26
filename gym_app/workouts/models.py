from django.db import models
from django.contrib.auth.models import User

class Muscle(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class Exercise(models.Model):
    name = models.CharField(max_length=100, unique=True)
    muscle = models.ForeignKey(Muscle, on_delete=models.CASCADE, related_name='exercises')
    equipment = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_exercises')
    likes = models.ManyToManyField(User, related_name='liked_exercises', blank=True)
    def __str__(self):
        return self.name

class Training(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trainings')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class TrainingExercise(models.Model):
    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name='exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.exercise.name} in {self.training.name}"

class TrainingSet(models.Model):
    training_exercise = models.ForeignKey(TrainingExercise, on_delete=models.CASCADE, related_name='sets')
    reps = models.IntegerField()
    weight = models.FloatField(default=0.0)
    def __str__(self):
        return f"Set for {self.training_exercise.exercise.name}: {self.reps} reps @ {self.weight}kg"

class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workouts')
    name = models.CharField(max_length=100, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.name or 'Workout'} - {self.user.username}"

class WorkoutExercise(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.exercise.name} in {self.workout}"

class WorkoutSet(models.Model):
    workout_exercise = models.ForeignKey(WorkoutExercise, on_delete=models.CASCADE, related_name='sets')
    reps = models.IntegerField()
    weight = models.FloatField()
    def __str__(self):
        return f"Set for {self.workout_exercise.exercise.name}: {self.reps} reps @ {self.weight}kg"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    workout_count = models.IntegerField(default=0)
    def __str__(self):
        return self.user.username