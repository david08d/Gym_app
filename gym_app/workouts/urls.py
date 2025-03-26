

from django.urls import path
from .views import ProtectedView, register

urlpatterns = [
    path('protected/', ProtectedView.as_view(), name='protected-view'),
    path('register/', register, name='register'),
]
