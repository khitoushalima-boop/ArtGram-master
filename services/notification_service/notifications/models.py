from django.db import models

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('LIKE', 'Like'),
        ('COMMENT', 'Comment'),
        ('FOLLOW', 'Follow'),
    )

    user_id = models.IntegerField()  # Recipient of the notification
    sender_id = models.IntegerField()  # User who triggered the notification
    artwork_id = models.IntegerField(null=True, blank=True)  # Optional reference to artwork
    type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for user {self.user_id}: {self.message}"
