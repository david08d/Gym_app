
from .models import Muscle, Exercise, Training, TrainingExercise, TrainingSet, Workout, WorkoutExercise, WorkoutSet, Profile
import requests
from django.contrib import admin
from .models import Exercise

admin.site.register(Muscle)
admin.site.register(Exercise)
admin.site.register(Training)
admin.site.register(TrainingExercise)
admin.site.register(TrainingSet)
admin.site.register(Workout)
admin.site.register(WorkoutExercise)
admin.site.register(WorkoutSet)
admin.site.register(Profile)

