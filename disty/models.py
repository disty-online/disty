from django.db import models

class Role(models.Model):
    role_name = models.CharField(max_length=50)

class User(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, db_index=True)
    password = models.CharField(max_length=100)