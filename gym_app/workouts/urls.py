from django.urls import path
from .views import ProtectedView, register, login_view, home_view, check_email_view, check_username_view, main_view, select_exercise_view
from . import views

urlpatterns = [
    path('', home_view, name='home'),
    path('protected/', ProtectedView.as_view(), name='protected-view'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('main/', main_view, name='main'),
    path('api/check-email/', check_email_view, name='check_email'),
    path('api/check-username/', check_username_view, name='check_username'),
    path('select-exercise/', views.select_exercise_view, name='select_exercise'),

]
