from django.db import models
import uuid


# Create your models here.

class User(models.Model):

    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, db_index = True)
    email = models.EmailField(unique = True)
    google_id = models.CharField(unique = True, null = True, blank = True)
    password = models.CharField(null = True, blank = True)
    full_name = models.CharField(max_length = 255)
    age = models.IntegerField(null = True, blank = True)
    address = models.CharField(max_length = 255, null = True, blank = True)
    phone = models.CharField(max_length = 15, null = True, blank = True)
    avatar_url = models.URLField(max_length=500, null=True, blank=True, default='/default-avatar.png')

    is_staff = models.BooleanField(default = False)
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    activation_token = models.CharField(blank = True, null = True, max_length = 255)
    activation_token_expires = models.TimeField(blank = True, null = True)

    reset_password_token = models.CharField(blank = True, null = True, max_length = 255)
    reset_password_expires = models.TimeField(blank = True, null = True)

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)


    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name_plural = "users"
