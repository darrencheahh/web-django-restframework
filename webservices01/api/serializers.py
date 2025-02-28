#change it to JSON data
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Professor, Module, Rating

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class ProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = '__all__'

class ModuleSerializer(serializers.ModelSerializer):
    professors = ProfessorSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = '__all__'

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'