from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin','admin'),
        ('customer','customer'),
    )
    role = models.CharField(choices=ROLE_CHOICES, max_length=50, default='customer')

    def __str__(self):
        return self.username

class Task(models.Model):
    TASK_TYPES = (
        ('ad', 'Ad'),
        ('music', 'Music'),
        ('podcast', 'Podcast'),
    )
    name = models.CharField(max_length=255)
    task_type = models.CharField(choices=TASK_TYPES, max_length=50)
    points = models.IntegerField()
    virtual_money = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    media_url = models.URLField(max_length=200,default="")  # URL for the media file

    def __str__(self):
        return self.name

class UserTask(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, max_length=50, default='pending')
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.task.name}"

class Reward(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    user_task = models.ForeignKey(UserTask, on_delete=models.CASCADE)
    points_earned = models.IntegerField()
    virtual_money_earned = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} - {self.points_earned} points - ${self.virtual_money_earned}"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('earn', 'Earn'),
        ('withdraw', 'Withdraw'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    transaction_type = models.CharField(choices=TRANSACTION_TYPES, max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - ${self.amount}"

class WithdrawalRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    points_required = models.IntegerField()
    amount_requested = models.DecimalField(max_digits=10, decimal_places=2)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - ${self.amount_requested} - {'Approved' if self.is_approved else 'Pending'}"
