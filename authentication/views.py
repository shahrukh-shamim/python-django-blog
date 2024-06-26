from django.shortcuts import render, redirect
from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views import View
from .models import User
from . import serializers
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
import sys

from django.http import HttpResponse

# Create your views here.

#SIGNUP view
class SignUpView(generics.GenericAPIView):
    signup_serializer=serializers.UserSignUpSerializer
    
    def post(self, request):
        data=request.data

        serializer = self.signup_serializer(data=data)

        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return_data = { "model": serializer.data, "message": "User created successfully", "access": {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            } }
            return Response(data=return_data, status=status.HTTP_201_CREATED)
        
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#LOGIN view
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        username = request.POST.get('email')
        password = request.POST.get('password')
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login user
            refresh = RefreshToken.for_user(user)
            return JsonResponse({'message': 'Login successful', 'data': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }})
        else:
            return JsonResponse({'message': 'Invalid credentials'}, status=400)

#SESSION BASE AUTH      
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST['username'] # you can use email, just change that in User model, the `USERNAME_FIELD` field
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return HttpResponse("Invalid credentials")
    return render(request, 'authentication/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')