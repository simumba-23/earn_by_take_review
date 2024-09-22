from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenVerifyView
from django.urls import path

from . import views
urlpatterns = [
   path('',views.getRoutes),
   path('api/token/', views.MyTokenObtainPairView.as_view()),
   path('api/token/refresh/', TokenRefreshView.as_view()),
   path('api/token/verify/', TokenVerifyView.as_view()),
  
 ]