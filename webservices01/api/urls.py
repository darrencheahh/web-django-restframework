from xml.etree.ElementInclude import include
from django.urls import path
from django.contrib import admin
from .views import *

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("modules/", ModuleListView.as_view(), name="module-list"),
    path("ratings/", ProfessorRatingView.as_view(), name="professor-rating"),
    path("ratings/<str:professor_id>/modules/<str:module_code>/rating/", ProfessorModuleRatingView.as_view(), name="professor-module-rating"),
    path("rate/", RateProfessorView.as_view(), name="rate-module"),
    path("professors/<str:professor_id>/", ProfessorDetailView.as_view(), name="professor-detail"),
    path("module/<str:module_code>/", ModuleDetailView.as_view(), name="module-detail"),
    path("module/<str:module_code>/<int:year>/<int:semester>/", ModuleDetailViewRate.as_view(), name="module-detail-rate"),
    path("admin/", admin.site.urls),
    path('api/', include('webservices01.urls')),
]