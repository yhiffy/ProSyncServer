from datetime import datetime

from django.db import models
import uuid

# Create your models here.

class User(models.Model):

    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, db_index = True)
    email = models.EmailField(unique = True)
    googleId = models.CharField(unique = True, null = True, blank = True)
    password = models.CharField(null = False, blank = False)
    fullName = models.CharField()
    age = models.IntegerField()
    address = models.CharField()
    phone = models.CharField()
    isStaff = models.BooleanField(default = False)
    activationToken = models.CharField()
    activationTokenExpires = models.TimeField("CURRENT_TIMESTAMP + interval '30 minutes'"))
    resetPasswordToken = models.BooleanField()
    resetPasswordExpires = models.TimeField(default = now)
    isActive = models.BooleanField(default = False)
    isDeleted = models.BooleanField(default = False)
    createdAt = models.DateTimeField(auto_now_add = True)
    updatedAt = models.DateTimeField(auto_now = True)


    def __str__(self):
        return self.email



