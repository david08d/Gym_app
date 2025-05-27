import json
import logging

from django.utils import timezone

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse, request
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.views.generic import DetailView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from .models import Exercise, Muscle, Profile, WorkoutSet, WorkoutExercise, Workout
from .serializers import UserRegisterSerializer
from rest_framework.authtoken.models import Token
from django.http import JsonResponse
from django.db.models import Q

def home_view(request):
    return render(request, 'workouts/home.html')

@login_required
def main_view(request):
    return render(request, 'workouts/main.html')

@login_required
def select_exercise_view(request):
    exercises = Exercise.objects.all()
    return render(request, 'workouts/select_exercise.html', {'exercises': exercises})

def start_workout_view(request):
    all_exercises = Exercise.objects.all()
    selected_ids = request.session.get('selected_ids', [])
    selected = Exercise.objects.filter(id__in=selected_ids)

    context = {
        'exercises': all_exercises,
        'selected_ids': selected_ids,
        'selected': selected
    }
    return render(request, 'workouts/start_workout.html', context)




logger = logging.getLogger(__name__)

@require_http_methods(["POST"])
def finish_workout(request):
    print("=" * 50)
    print("FINISH_WORKOUT VIEW CALLED!")
    print(f"Request method: {request.method}")
    print(f"Request path: {request.path}")
    print(f"User: {request.user}")
    print(f"User authenticated: {request.user.is_authenticated}")
    print("=" * 50)

    if not request.user.is_authenticated:
        print("User not authenticated, returning 401")
        return JsonResponse({
            'status': 'error',
            'error': 'Authentication required'
        }, status=401)

    try:
        logger.info(f"Received workout data from user: {request.user.username}")
        logger.info(f"Request content type: {request.content_type}")
        logger.info(f"Request body: {request.body}")

        if not request.body:
            logger.error("Empty request body")
            return JsonResponse({
                'status': 'error',
                'error': 'No data received'
            }, status=400)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return JsonResponse({
                'status': 'error',
                'error': f'Invalid JSON data: {str(e)}'
            }, status=400)

        workout_data = data.get('workoutData', [])
        logger.info(f"Parsed workout data: {workout_data}")

        if not workout_data:
            logger.error("No workout data provided")
            return JsonResponse({
                'status': 'error',
                'error': 'No workout data provided'
            }, status=400)

        
        workout = Workout.objects.create(
            user=request.user,
            name=f"Workout {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            start_time=timezone.now(),
            end_time=timezone.now(),
            completed=True
        )
        logger.info(f"Created workout with ID: {workout.id}")

        exercises_processed = 0
        sets_processed = 0

        for exercise_data in workout_data:
            exercise_name = exercise_data.get('exerciseName')
            sets_data = exercise_data.get('sets', [])

            logger.info(f"Processing exercise: {exercise_name} with {len(sets_data)} sets")

            if not exercise_name or not sets_data:
                logger.warning(f"Skipping exercise due to missing data: {exercise_name}")
                continue

            try:
                exercise = Exercise.objects.get(name=exercise_name)
                logger.info(f"Found exercise: {exercise.name}")
            except Exercise.DoesNotExist:
                try:
                    exercise = Exercise.objects.create(
                        name=exercise_name,
                        type="custom",
                        muscle="unknown",
                        equipment="unknown",
                        created_by=request.user
                    )
                    logger.info(f"Created new exercise: {exercise.name}")
                except Exception as e:
                    logger.error(f"Error creating exercise: {e}")
                    continue

            try:
                workout_exercise = WorkoutExercise.objects.create(
                    workout=workout,
                    exercise=exercise
                )
                exercises_processed += 1
                logger.info(f"Created workout exercise with ID: {workout_exercise.id}")
            except Exception as e:
                logger.error(f"Error creating workout exercise: {e}")
                continue

            for i, set_data in enumerate(sets_data):
                try:
                    reps = set_data.get('reps')
                    weight = set_data.get('weight')

                    logger.info(f"Processing set {i + 1}: {reps} reps, {weight} kg")

                    if reps and weight:
                        workout_set = WorkoutSet.objects.create(
                            workout_exercise=workout_exercise,
                            reps=int(reps),
                            weight=float(weight)
                        )
                        sets_processed += 1
                        logger.info(f"Created workout set with ID: {workout_set.id}")
                except Exception as e:
                    logger.error(f"Error creating workout set: {e}")
                    continue

        try:
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.workout_count += 1
            profile.save()
            logger.info(f"Updated profile workout count to: {profile.workout_count}")
        except Exception as e:
            logger.error(f"Error updating profile: {e}")

        logger.info(f"Workout completed: {exercises_processed} exercises, {sets_processed} sets")

        request.session['selected_ids'] = []

        response_data = {
            'status': 'success',
            'message': 'Workout saved successfully',
            'workout_id': workout.id,
            'exercises_processed': exercises_processed,
            'sets_processed': sets_processed,
            'redirect': '/main/'
        }

        print("=" * 30)
        print("RETURNING SUCCESS RESPONSE:")
        print(response_data)
        print("=" * 30)

        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"Unexpected error in finish_workout: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

        error_response = {
            'status': 'error',
            'error': f'An error occurred: {str(e)}'
        }

        print("=" * 30)
        print("RETURNING ERROR RESPONSE:")
        print(error_response)
        print("=" * 30)

        return JsonResponse(error_response, status=500)

@require_POST
def add_exercise(request, exercise_id):
    selected = request.session.get('selected_ids', [])
    if exercise_id not in selected:
        selected.append(exercise_id)
    request.session['selected_ids'] = selected
    return JsonResponse({'status': 'ok'})

@login_required
class ExerciseDetailView(DetailView):
    model = Exercise
    template_name = 'workouts/exercise_detail.html'
    context_object_name = 'exercise'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get similar exercises by same muscle
        context['similar_exercises'] = Exercise.objects.filter(
            muscle=self.object.muscle
        ).exclude(id=self.object.id)[:4]
        return context

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "You have access to this protected view!"})

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def check_username_view(request):
    username = request.GET.get('username')
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def check_email_view(request):
    email = request.GET.get('email')
    exists = User.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def register(request):
    if request.method == 'GET':
        return render(request, 'workouts/register.html')
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        login(request, user)
        return JsonResponse({
            "success": True,
            "message": "User created successfully!",
            "token": token.key,
            "redirect": "/main/"
        })
    
    errors = {}
    if 'username' in serializer.errors:
        errors['username'] = 'Username is already taken'
    if 'email' in serializer.errors:
        errors['email'] = 'Email is already registered'
    return JsonResponse({
        "success": False,
        "errors": errors
    }, status=400)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def login_view(request):
    if request.method == 'GET':
        return render(request, 'workouts/login.html')

    email = request.data.get('email')
    password = request.data.get('password')
    
    try:
        user = User.objects.get(email=email)
        if user.check_password(password):
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return JsonResponse({
                'success': True,
                'token': token.key,
                'redirect': '/main/'
            })
    except User.DoesNotExist:
        pass
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid email or password'
    }, status=401)


@api_view(['GET'])
def get_users(request):
    users = User.objects.all()
    serializer = UserRegisterSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['PUT'])
def update_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserRegisterSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User updated successfully!"})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return Response({"message": "User deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@login_required
def exercise_page(request):
    search_query = request.GET.get('search')

    if search_query:
        exercises = Exercise.objects.filter(
            Q(name__icontains=search_query) |
            Q(muscle__icontains=search_query)
        )
        categories = {}
        for exercise in exercises:
            part = exercise.body_part or "Other"
            categories.setdefault(part, []).append({
                'name': exercise.name,
                'muscle': exercise.muscle,
                'gif_url': exercise.gif_url
            })

        return JsonResponse({'categories': categories})
    popular_exercises = Exercise.objects.annotate(
        like_count=Count('likes')
    ).order_by('-like_count')[:5]

    body_parts = Exercise.objects.values_list('body_part', flat=True).distinct()
    categories = []
    for body_part in body_parts:
        if body_part:
            category = {
                'name': body_part.title(),
                'exercises': Exercise.objects.filter(body_part=body_part)[:20]
            }
            categories.append(category)

    context = {
        'popular_exercises': popular_exercises,
        'categories': categories,
        'request': request,
    }

    return render(request, 'workouts/exercise.html', context)


def exercise_detail(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    return render(request, 'workouts/exercise_detail.html', {'exercise': exercise})



def logout_view(request):
    logout(request)
    return render(request, 'workouts/home.html')

@login_required
def profile_page(request):
    if request.method == 'POST':
        photo = request.FILES.get('profile_image')
        if photo:
            profile = request.user.profile
            profile.photo = photo
            profile.save()
    
    # Отримуємо завершені тренування (completed=True або end_time не None)
    completed_workouts = Workout.objects.filter(
        user=request.user
    ).filter(
        Q(completed=True) | Q(end_time__isnull=False)
    ).order_by('-start_time')[:5]
    
    # Підраховуємо загальну кількість виконаних вправ
    total_exercises = WorkoutExercise.objects.filter(
        workout__in=Workout.objects.filter(
            user=request.user
        ).filter(
            Q(completed=True) | Q(end_time__isnull=False)
        )
    ).count()
    
    workout_details = []
    
    for workout in completed_workouts:
        exercises = WorkoutExercise.objects.filter(workout=workout)
        exercise_details = []
        
        for workout_exercise in exercises:
            sets = WorkoutSet.objects.filter(workout_exercise=workout_exercise).order_by('id')
            if sets.exists():
                sets_info = []
                for set in sets:
                    sets_info.append({
                        'reps': set.reps,
                        'weight': set.weight
                    })
                exercise_details.append({
                    'name': workout_exercise.exercise.name,
                    'muscle': workout_exercise.exercise.muscle,
                    'is_favorite': workout_exercise.exercise in request.user.profile.favorite_exercises.all(),
                    'sets': sets_info
                })
        
        # Розраховуємо тривалість тренування
        duration = None
        if workout.end_time and workout.start_time:
            duration = int((workout.end_time - workout.start_time).total_seconds() / 60)
        
        workout_details.append({
            'id': workout.id,
            'name': workout.name,
            'start_time': workout.start_time,
            'duration': duration,
            'exercises': exercise_details
        })

    context = {
        'user': request.user,
        'workout_details': workout_details,
        'completed_workouts_count': Workout.objects.filter(
            user=request.user
        ).filter(
            Q(completed=True) | Q(end_time__isnull=False)
        ).count(),
        'favorite_exercises_count': request.user.profile.favorite_exercises.count(),
        'total_exercises': total_exercises
    }
    
    return render(request, 'workouts/profile.html', context)




@login_required
def favorite_exercises(request):
    favorite_exercises = request.user.profile.favorite_exercises.all()
    exercises_data = []
    
    for exercise in favorite_exercises:
        exercises_data.append({
            'id': exercise.id,
            'name': exercise.name,
            'muscle': exercise.muscle,
            'gif_url': exercise.gif_url
        })
    
    return render(request, 'workouts/favorite_exercises.html', {
        'favorite_exercises': exercises_data
    })

@login_required
@require_POST
def toggle_favorite(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id)
    profile = request.user.profile
    if exercise in profile.favorite_exercises.all():
        profile.favorite_exercises.remove(exercise)
        return JsonResponse({'success': True, 'action': 'removed'})
    else:
        profile.favorite_exercises.add(exercise)
        return JsonResponse({'success': True, 'action': 'added'})

@login_required
def workout_detail(request, workout_id):
    # Отримуємо всі завершені тренування користувача
    workouts = Workout.objects.filter(
        user=request.user
    ).filter(
        Q(completed=True) | Q(end_time__isnull=False)
    ).order_by('-start_time')
    
    workout_details = []
    
    for workout in workouts:
        exercises = WorkoutExercise.objects.filter(workout=workout)
        exercise_details = []
        
        for workout_exercise in exercises:
            sets = WorkoutSet.objects.filter(workout_exercise=workout_exercise).order_by('id')
            if sets.exists():
                sets_info = []
                for set in sets:
                    sets_info.append({
                        'id': set.id,
                        'reps': set.reps,
                        'weight': set.weight
                    })
                exercise_details.append({
                    'id': workout_exercise.id,
                    'name': workout_exercise.exercise.name,
                    'muscle': workout_exercise.exercise.muscle,
                    'sets': sets_info
                })
        
        # Розраховуємо тривалість тренування
        duration = None
        if workout.end_time and workout.start_time:
            duration = int((workout.end_time - workout.start_time).total_seconds() / 60)
        
        workout_details.append({
            'id': workout.id,
            'name': workout.name,
            'start_time': workout.start_time,
            'duration': duration,
            'exercises': exercise_details
        })
    
    context = {
        'workouts': workout_details
    }
    
    return render(request, 'workouts/workout_detail.html', context)