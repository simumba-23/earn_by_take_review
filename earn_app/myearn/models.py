from django.db import models
from django.contrib.auth.models import AbstractUser
# from datetime import timedelta,timezone
from django.utils import timezone


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin','admin'),
        ('customer','customer'),
    )
    role = models.CharField(choices=ROLE_CHOICES, max_length=50, default='customer')
    phone_number = models.CharField(max_length=25)
    sex = models.CharField(max_length=25)

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
    is_active = models.BooleanField(default=True)
    media_url = models.URLField(max_length=200,default="")  # URL for the media file
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Survey(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

class Question(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    text = models.TextField()
    is_multiple_choice = models.BooleanField(default=False)

    def __str__(self):
        return self.text
class AnswerOption(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

class UserTask(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, max_length=50, default='Pending')
    points_earned = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} - {self.task.name}"
    
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    selected_option = models.ForeignKey(AnswerOption, on_delete=models.CASCADE, null=True, blank=True)
    user_task = models.ForeignKey(UserTask,on_delete= models.CASCADE)

    def __str__(self):
        return self.selected_option.text if self.selected_option else "No Answer"

class VirtualWallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username}'s Wallet - Balance: ${self.balance}"

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
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    account_details = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='pending')  # 'pending', 'approved', 'rejected'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PointsConversionRate(models.Model):
    rate = models.DecimalField(max_digits=10, decimal_places=4)  # e.g., 0.01 for 1 point = $0.01
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name
class Tag(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name
class Blog(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    categories = models.ManyToManyField(Category, related_name='blogs')
    tags = models.ManyToManyField(Tag, related_name='blogs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.blog.title}"
