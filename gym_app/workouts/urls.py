from django.urls import path
from .views import ProtectedView, register, login_view, home_view, check_email_view, exercise_page, check_username_view, main_view, select_exercise_view, ExerciseDetailView, profile_page
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', home_view, name='home'),
    path('protected/', ProtectedView.as_view(), name='protected-view'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('main/', main_view, name='main'),
    path('exercise/', views.exercise_page, name='exercise_page'),
    path('exercise/<int:pk>/', views.exercise_detail, name='exercise_detail'),
    path('profile/', views.profile_page, name='profile_page'),
    path('start-workout/', views.start_workout_view, name='start_workout'),
    path('add-exercise/<int:exercise_id>/', views.add_exercise, name='add_exercise'),
    path('finish-workout/', views.finish_workout, name='finish_workout'),
    path('logout/', views.logout_view, name='logout'),
    path('api/check-email/', check_email_view, name='check_email'),
    path('api/check-username/', check_username_view, name='check_username'),
    path('select-exercise/', views.select_exercise_view, name='select_exercise'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
