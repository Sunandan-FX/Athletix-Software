from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from .forms import SignUpForm, LoginForm, ForgotPasswordForm, ResetPasswordForm, ProfileEditForm
from .models import User, AthleteProfile, CoachProfile, MedicalProfile


def home_view(request):
    return render(request, 'home.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()

            if user.role == 'athlete':
                AthleteProfile.objects.create(user=user)
            elif user.role == 'coach':
                CoachProfile.objects.create(user=user)
            elif user.role == 'medical':
                MedicalProfile.objects.create(user=user)

            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()

    return render(request, 'user/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        # Redirect to role-specific dashboard
        if request.user.role == 'athlete':
            return redirect('player:dashboard')
        elif request.user.role == 'coach':
            return redirect('coach:dashboard')
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    if user.is_active:
                        login(request, user)
                        messages.success(request, f'Welcome back, {user.first_name}!')
                        # Redirect to role-specific dashboard
                        if user.role == 'athlete':
                            return redirect('player:dashboard')
                        elif user.role == 'coach':
                            return redirect('coach:dashboard')
                        return redirect('dashboard')
                    else:
                        messages.error(request, 'Your account has been deactivated.')
                else:
                    messages.error(request, 'Invalid email or password.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()

    return render(request, 'user/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def forgot_password_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password updated successfully! Please log in with your new password.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email address.')
    else:
        form = ForgotPasswordForm()

    return render(request, 'user/forget_password.html', {'form': form})


def reset_password_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = ResetPasswordForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                messages.success(request, 'Password reset successful! Please log in.')
                return redirect('login')
        else:
            form = ResetPasswordForm()

        return render(request, 'user/password_reset_confirm.html', {
            'form': form,
            'uidb64': uidb64,
            'token': token
        })
    else:
        messages.error(request, 'The password reset link is invalid or has expired.')
        return redirect('forgot_password')


@login_required
def dashboard_view(request):
    """Redirect to role-specific dashboard or show generic dashboard"""
    user = request.user
    
    # Redirect athletes to player dashboard
    if user.role == 'athlete':
        return redirect('player:dashboard')
    # Redirect coaches to coach dashboard
    elif user.role == 'coach':
        return redirect('coach:dashboard')
    
    # For medical staff or others, show generic dashboard
    context = {'user': user}
    if user.role == 'medical':
        try:
            context['profile'] = user.medical_profile
        except MedicalProfile.DoesNotExist:
            context['profile'] = None

    return render(request, 'user/dashboard.html', context)


@login_required
def profile_view(request):
    user = request.user
    context = {'user': user}

    if user.role == 'athlete':
        try:
            context['role_profile'] = user.athlete_profile
        except AthleteProfile.DoesNotExist:
            context['role_profile'] = None
    elif user.role == 'coach':
        try:
            context['role_profile'] = user.coach_profile
        except CoachProfile.DoesNotExist:
            context['role_profile'] = None
    elif user.role == 'medical':
        try:
            context['role_profile'] = user.medical_profile
        except MedicalProfile.DoesNotExist:
            context['role_profile'] = None

    return render(request, 'user/profile.html', context)


@login_required
def profile_edit_view(request):
    user = request.user

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileEditForm(instance=user)

    return render(request, 'user/profile_edit.html', {'form': form})