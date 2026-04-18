from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notifications_view(request):
    notifications = request.user.notifications.all()
    return render(request, 'notifications.html', {'notifications': notifications})

@login_required
def mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications:home')
