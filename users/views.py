from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.contrib import messages
import json
from .models import User
from .forms import CustomUserCreationForm


# ═══════════════════════════════════════════════════════════════════════════
# TRADITIONAL FORM-BASED AUTHENTICATION (Server-side rendering)
# ═══════════════════════════════════════════════════════════════════════════

@ensure_csrf_cookie
def login_signup_view(request):
    """
    Combined login/signup view with proper session handling.
    ✅ CSRF token automatically available
    ✅ Sessions properly created after login
    ✅ Redirects to authenticated page after successful login
    """
    if request.user.is_authenticated:
        return redirect('artworks:home')
        
    login_form = AuthenticationForm()
    signup_form = CustomUserCreationForm()
    
    if request.method == 'POST':
        if 'login' in request.POST:
            login_form = AuthenticationForm(data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)  # ✅ Creates session
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('artworks:home')
            else:
                messages.error(request, 'Invalid username or password.')
                
        elif 'signup' in request.POST:
            signup_form = CustomUserCreationForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                login(request, user)  # ✅ Creates session after registration
                messages.success(request, f'Welcome to ArtGram, {user.username}!')
                return redirect('artworks:home')
            else:
                for field, errors in signup_form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
                
    return render(request, 'log.html', {
        'login_form': login_form,
        'signup_form': signup_form
    })

def logout_view(request):
    """Logout user and destroy session."""
    logout(request)  # ✅ Clears session
    messages.success(request, 'You have been logged out.')
    return redirect('artworks:home')

@login_required(login_url='users:auth')
def profile_view(request, username):
    """Protected view - only logged-in users can access."""
    user_profile = get_object_or_404(User, username=username)
    is_following = False
    if request.user.is_authenticated and request.user != user_profile:
        is_following = request.user.following.filter(following=user_profile).exists()
        
    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'is_following': is_following
    })


# ═══════════════════════════════════════════════════════════════════════════
# JSON API ENDPOINTS (For frontend-backend JSON communication)
# ═══════════════════════════════════════════════════════════════════════════

@require_http_methods(["GET"])
@ensure_csrf_cookie
def api_csrf_token(request):
    """
    Endpoint to retrieve CSRF token for frontend.
    Called by frontend on page load to get token for subsequent requests.
    """
    token = get_token(request)
    return JsonResponse({
        'csrfToken': token,
        'detail': 'CSRF token retrieved successfully'
    })


@require_http_methods(["POST"])
@csrf_protect
def api_login(request):
    """
    JSON API endpoint for login.
    ✅ Accepts JSON payload
    ✅ Returns JSON response
    ✅ Creates session automatically
    ✅ No redirect needed (frontend handles navigation)
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({
                'ok': False,
                'detail': 'Username and password are required'
            }, status=400)

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login user and create session ✅
            login(request, user)
            
            return JsonResponse({
                'ok': True,
                'detail': f'Login successful. Welcome {user.username}!',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_authenticated': True
                }
            }, status=200)
        else:
            return JsonResponse({
                'ok': False,
                'detail': 'Invalid username or password'
            }, status=401)

    except json.JSONDecodeError:
        return JsonResponse({
            'ok': False,
            'detail': 'Invalid JSON payload'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'ok': False,
            'detail': f'Login error: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
@csrf_protect
def api_register(request):
    """
    JSON API endpoint for registration.
    ✅ Accepts JSON payload
    ✅ Returns JSON response
    ✅ Creates user and session
    """
    try:
        data = json.loads(request.body)
        
        # Extract data
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validate input
        if not all([username, email, password]):
            return JsonResponse({
                'ok': False,
                'detail': 'Username, email, and password are required'
            }, status=400)
        
        # Check if user exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'ok': False,
                'detail': 'Username already exists'
            }, status=409)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'ok': False,
                'detail': 'Email already registered'
            }, status=409)
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Auto-login after registration ✅
        login(request, user)
        
        return JsonResponse({
            'ok': True,
            'detail': 'Registration successful!',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_authenticated': True
            }
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({
            'ok': False,
            'detail': 'Invalid JSON payload'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'ok': False,
            'detail': f'Registration error: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
@csrf_protect
def api_logout(request):
    """
    JSON API endpoint for logout.
    ✅ Destroys session
    ✅ Returns JSON response
    """
    try:
        logout(request)
        return JsonResponse({
            'ok': True,
            'detail': 'Logout successful'
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'ok': False,
            'detail': f'Logout error: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def api_user_profile(request):
    """
    JSON API endpoint to get current user profile.
    ✅ Requires authentication
    ✅ Returns user data as JSON
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'ok': False,
            'detail': 'Not authenticated'
        }, status=401)
    
    try:
        user = request.user
        return JsonResponse({
            'ok': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_authenticated': True
            }
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'ok': False,
            'detail': f'Error fetching profile: {str(e)}'
        }, status=500)
