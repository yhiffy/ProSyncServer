from datetime import timedelta

from django.db import models
import uuid

from django.utils import timezone


# Create your models here.

class User(models.Model):

    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, db_index = True)
    email = models.EmailField(unique = True)
    googleId = models.CharField(unique = True, null = True, blank = True)
    password = models.CharField(null = False, blank = False)
    fullName = models.CharField(max_length = 255)
    age = models.IntegerField()
    address = models.CharField(max_length = 255)
    phone = models.CharField(max_length = 15)

    isStaff = models.BooleanField(default = False)
    isActive = models.BooleanField(default=False)
    isDeleted = models.BooleanField(default=False)

    activationToken = models.CharField()
    activationTokenExpires = models.DateTimeField(default = timezone.now() + timedelta(minutes = 30))

    resetPasswordToken = models.BooleanField()
    resetPasswordExpires = models.TimeField()

    createdAt = models.DateTimeField(auto_now_add = True)
    updatedAt = models.DateTimeField(auto_now = True)


    def __str__(self):
        return self.email

    class Meta:
        verbose_name_plural = "users"



