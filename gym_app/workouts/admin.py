from .models import Muscle, Exercise, Training, TrainingExercise, TrainingSet, Workout, WorkoutExercise, WorkoutSet, Profile
import requests
from django.contrib import admin
from .models import Exercise

admin.site.register(Muscle)

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'muscle', 'equipment', 'created_by')
    search_fields = ('name', 'muscle', 'type')
    list_filter = ('type', 'muscle', 'equipment')

admin.site.register(Training)
admin.site.register(TrainingExercise)
admin.site.register(TrainingSet)

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'start_time', 'end_time', 'completed')
    list_filter = ('completed', 'user')
    search_fields = ('name', 'user__username')

@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    list_display = ('workout', 'exercise')
    list_filter = ('workout', 'exercise')

@admin.register(WorkoutSet)
class WorkoutSetAdmin(admin.ModelAdmin):
    list_display = ('workout_exercise', 'reps', 'weight')
    list_filter = ('workout_exercise__workout',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'workout_count')
    search_fields = ('user__username',)

