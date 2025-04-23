from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from .serializers import UserRegisterSerializer
from rest_framework.authtoken.models import Token

def home_view(request):
    return render(request, 'workouts/home.html')

@login_required
def main_view(request):
    return render(request, 'workouts/main.html')

@login_required
def select_exercise_view(request):
    return render(request, 'workouts/select_exercise.html')

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
