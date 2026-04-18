from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from artworks.models import Artwork
from .models import Like, Comment, Follow
from users.models import User
from notifications.models import Notification

@login_required
def like_artwork(request, artwork_id):
    artwork = get_object_or_404(Artwork, id=artwork_id)
    like, created = Like.objects.get_or_create(user=request.user, artwork=artwork)
    if not created:
        like.delete()
    else:
        Notification.objects.create(
            recipient=artwork.user,
            sender=request.user,
            notification_type='like',
            artwork=artwork
        )
    return redirect(request.META.get('HTTP_REFERER', 'artworks:home'))

@login_required
def comment_artwork(request, artwork_id):
    if request.method == 'POST':
        artwork = get_object_or_404(Artwork, id=artwork_id)
        text = request.POST.get('text')
        if text:
            Comment.objects.create(user=request.user, artwork=artwork, text=text)
            Notification.objects.create(
                recipient=artwork.user,
                sender=request.user,
                notification_type='comment',
                artwork=artwork
            )
    return redirect(request.META.get('HTTP_REFERER', 'artworks:home'))

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if user_to_follow != request.user:
        follow, created = Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
        if not created:
            follow.delete()
        else:
            Notification.objects.create(
                recipient=user_to_follow,
                sender=request.user,
                notification_type='follow'
            )
    return redirect('users:profile', username=username)
