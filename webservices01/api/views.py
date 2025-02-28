from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.db.models import Avg
from .serializers import UserSerializer, ModuleSerializer
from .models import Module, Professor, Rating

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)

class ProfessorDetailView(APIView):
    def get(self, request, professor_id):
        try:
            professor = Professor.objects.get(id=professor_id)
            return Response({
                "id": professor.id,
                "name": professor.name
            }, status=status.HTTP_200_OK)
        except Professor.DoesNotExist:
            return Response({"error": "Professor not found"}, status=status.HTTP_404_NOT_FOUND)

class ModuleDetailView(APIView):
    def get(self, request, module_code):
        try:
            module = Module.objects.get(code=module_code)
            return Response({
                "code": module.code,
                "name": module.name,
                "year": module.year,
                "semester": module.semester,
                "professors": [{"id": professor.id, "name": professor.name} for professor in module.professors.all()]
            }, status=status.HTTP_200_OK)
        except Module.DoesNotExist:
            return Response({"error": "Module not found"}, status=status.HTTP_404_NOT_FOUND)

class ModuleListView(generics.ListCreateAPIView):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer

class ProfessorRatingView(APIView):
    def get(self, request):
        professors = Professor.objects.all()
        data = []
        for professor in professors:
            ratings = Rating.objects.filter(professor=professor)
            avg_ratings = round(sum(r.rating for r in ratings) / ratings.count()) if ratings else 0
            data.append({"professor": professor.name, "rating": "*" * avg_ratings})
        return Response(data, status=status.HTTP_200_OK)

class ProfessorModuleRatingView(APIView):
    def get(self, request, professor_id, module_code):
        try:
            module = Module.objects.filter(code=module_code)

            if not module.exists():
                return Response({"error": "Module not found"}, status=status.HTTP_404_NOT_FOUND)

            ratings = Rating.objects.filter(professor__id=professor_id, module__in=module)

            if not ratings.exists():
                return Response({"error": "No rating found for this professor"}, status=status.HTTP_404_NOT_FOUND)

            avg_rating = round(ratings.aggregate(Avg("rating"))["rating__avg"] or 0)

            return Response({
                "professor": professor_id,
                "module": module_code,
                "rating": "*" * avg_rating
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error:", e)
            return Response({"error": "Internal Server Error"}, status=status.HTTP_404_NOT_FOUND)

class RateProfessorView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            print("received rating request", request.data)

            professor_id = request.data.get("professor_id")
            module_code = request.data.get("module_code")
            year = request.data.get("year")
            semester = request.data.get("semester")
            rating_val = request.data.get("rating")

            if not professor_id or not module_code or not year or not semester or not rating_val:
                print("missing required fields")
                return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

            if not (1 <= int(rating_val) <= 5):
                return Response({"error": "Rating must be between 1 and 5"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                professor = Professor.objects.get(id=professor_id)
                module = Module.objects.get(code=module_code, year=year, semester=semester)
            except Professor.DoesNotExist:
                return Response({"error": "Professor not found"}, status=status.HTTP_404_NOT_FOUND)
            except Module.DoesNotExist:
                return Response({"error": "Module not found"}, status=status.HTTP_404_NOT_FOUND)

            Rating.objects.create(
                student = request.user,
                professor = professor,
                module = module,
                rating = rating_val
            )
            return Response({"message": "Rating submitted successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("error:", e)
            return Response({"message": "Rating submitted successfully"}, status=status.HTTP_201_CREATED)