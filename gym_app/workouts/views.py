from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse, request
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from .models import Exercise, Muscle, Profile
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
    }

    return render(request, 'workouts/exercise.html', context)


def exercise_detail(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    return render(request, 'workouts/exercise_detail.html', {'exercise': exercise})

# def profile_page(request):
#     return render(request, 'workouts/profile.html')

def logout_view(request):
    logout(request)
    return render(request, 'workouts/home.html')

login_required
def profile_page(request):
    if request.method == 'POST':
        photo = request.FILES.get('profile_image')
        if photo:
            profile = request.user.profile
            profile.photo = photo
            profile.save()
        return render(request, ('workouts/profile.html'))  # або ім'я URL сторінки профілю

    return render(request, 'workouts/profile.html')
