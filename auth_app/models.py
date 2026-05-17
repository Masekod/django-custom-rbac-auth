from django.db import models

class User(models.Model):
    objects = models.Manager()

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True) # Для мягкого удаления
    created_at = models.DateTimeField(auto_now_add=True)

class Role(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=50, unique=True) # Admin, User

class UserRole(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

class Resource(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=100, unique=True) # "documents", "reports"

class Action(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=50, unique=True) # "create", "read", "update"

class Permission(models.Model):
    objects = models.Manager()
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
