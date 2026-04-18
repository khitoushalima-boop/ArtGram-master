from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import User
from .forms import CustomUserCreationForm
from django.contrib import messages

def login_signup_view(request):
    if request.user.is_authenticated:
        return redirect('artworks:home')
        
    login_form = AuthenticationForm()
    signup_form = CustomUserCreationForm()
    
    if request.method == 'POST':
        if 'login' in request.POST:
            login_form = AuthenticationForm(data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect('artworks:home')
        elif 'signup' in request.POST:
            signup_form = CustomUserCreationForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                login(request, user)
                return redirect('artworks:home')
                
    return render(request, 'log.html', {
        'login_form': login_form,
        'signup_form': signup_form
    })

def logout_view(request):
    logout(request)
    return redirect('artworks:home')

def profile_view(request, username):
    user_profile = get_object_or_404(User, username=username)
    is_following = False
    if request.user.is_authenticated and request.user != user_profile:
        is_following = request.user.following.filter(following=user_profile).exists()
        
    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'is_following': is_following
    })
