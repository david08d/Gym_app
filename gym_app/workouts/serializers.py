from django.contrib.auth.models import User
from rest_framework import serializers
import re

class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Користувач з таким email вже існує.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Користувач з таким ім'ям вже існує.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Пароль має містити щонайменше 8 символів.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Пароль повинен містити хоча б одну ВЕЛИКУ літеру.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Пароль повинен містити хоча б одну маленьку літеру.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Пароль повинен містити хоча б одну цифру.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Пароль повинен містити хоча б один спеціальний символ.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
