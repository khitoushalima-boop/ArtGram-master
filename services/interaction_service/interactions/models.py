from django.db import models

class Like(models.Model):
    user_id = models.IntegerField()  # Reference to user_id from User Service
    artwork_id = models.IntegerField()  # Reference to artwork_id from Artwork Service
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_id', 'artwork_id')

    def __str__(self):
        return f"Like by user {self.user_id} on artwork {self.artwork_id}"

class Comment(models.Model):
    user_id = models.IntegerField()  # Reference to user_id from User Service
    artwork_id = models.IntegerField()  # Reference to artwork_id from Artwork Service
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by user {self.user_id} on artwork {self.artwork_id}"
