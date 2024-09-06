from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
# from datetime import timedelta,timezone
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
import string
from django.utils.text import slugify
from decimal import Decimal

POINTS_TO_MONEY_CONVERSION_RATE = Decimal('0.0029')


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin','admin'),
        ('customer','customer'),
    )
    role = models.CharField(choices=ROLE_CHOICES, max_length=50, default='customer')
    phone_number = models.CharField(max_length=25)
    image_url = models.ImageField(upload_to='profiles')
    sex = models.CharField(max_length=25)
    otp_secret = models.CharField(max_length=32, blank=True, null=True)
    is_2fa_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Task(models.Model):
    TASK_TYPES = (
        ('Video', 'Video'),
        ('Podcast', 'Podcast'),
        ('Audio', 'Audio'),
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
    
    def convert_points_to_money(self):
        return Decimal(self.points_earned) * POINTS_TO_MONEY_CONVERSION_RATE
    
    def handle_referral_reward(self):
        if self.status == 'Completed':
            # Get referral for the user
            try:
                referral = Referral.objects.get(invitee=self.user)
                reward_amount = self.convert_points_to_money() * Decimal('0.20')
                # Create referral reward
                ReferralReward.objects.create(user=referral.inviter, amount=reward_amount, reason=f"Referral reward for {self.user.username}'s task completion")
                
                # Update the inviter's wallet
                wallet, created = VirtualWallet.objects.get_or_create(user=referral.inviter)
                wallet.update_balance(reward_amount)
                
                # Log the referral reward transaction
                TransactionHistory.log_transaction(
                    user=referral.inviter,
                    transaction_type='Referral Reward',
                    amount=reward_amount,
                    description=f"Referral reward for {self.user.username}'s task completion"
                )
            except Referral.DoesNotExist:
                # No referral found
                pass
class EarningHistory(models.Model):
    user_task = models.OneToOneField(UserTask, on_delete=models.CASCADE, related_name='earning_history')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='earning_histories')
    points_earned = models.IntegerField()
    money_earned = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Earning History for {self.user.username} - {self.points_earned} points"

    @staticmethod
    def create_history(user_task):
        if user_task.status == 'Completed':
            money_earned = user_task.convert_points_to_money()
            EarningHistory.objects.create(
                user_task=user_task,
                user=user_task.user,
                points_earned=user_task.points_earned,
                money_earned=money_earned
            )

class TransactionHistory(models.Model):
    TRANSACTION_TYPES = (
        ('Earning', 'Earning'),
        ('Withdrawal', 'Withdrawal'),
        ('Referral Reward', 'Referral Reward'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transaction_histories')
    transaction_type = models.CharField(choices=TRANSACTION_TYPES, max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - ${self.amount}"

    @staticmethod
    def log_transaction(user, transaction_type, amount, description):
        TransactionHistory.objects.create(
            user=user,
            transaction_type=transaction_type,
            amount=amount,
            description=description
        )


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
    
    def update_balance(self, amount):
        self.balance += Decimal(amount)
        # print(amount)
        self.save()

@receiver(post_save, sender=UserTask)
def update_wallet_balance(sender, instance, **kwargs):
    if instance.status == 'Completed':
        wallet, created = VirtualWallet.objects.get_or_create(user=instance.user)
        amount_earned = instance.convert_points_to_money()
        wallet.update_balance(amount_earned)

        # Log the earning transaction
        TransactionHistory.log_transaction(
            user=instance.user,
            transaction_type='Earning',
            amount=amount_earned,
            description=f"Earned from task {instance.task.name}"
        )
        # Create earning history record
        EarningHistory.create_history(instance)
        
        # Handle referral reward
        instance.handle_referral_reward()

class WithdrawalRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} $ {self.amount}"
        
    def validate_withdrawal_day(self):
        today = timezone.now().weekday()
        if today not in [0,1,2,3,4 ]:  # 0: Monday, 4: friday
            raise ValidationError("Withdrawals are only allowed from Monday to Friday.")

    def validate_minimum_amount(self):
        # Check if this is the user's first withdrawal
        first_withdrawal = not WithdrawalRequest.objects.filter(user=self.user).exists()
        if first_withdrawal and self.amount < Decimal('5.00'):
            raise ValidationError("The minimum withdrawal amount for the first withdrawal is $ 5.")

    def validate_invitation_count(self):
        if not WithdrawalRequest.objects.filter(user=self.user).exists():
            # No need to validate invitations for the first withdrawal
            return
        # Check if the user has invited at least 15 people
        invite_count = Referral.objects.filter(inviter=self.user).count()
        if invite_count < 15:
            raise ValidationError("You must invite at least 15 people for subsequent withdrawals.")

    def clean(self):
        self.validate_withdrawal_day()
        self.validate_minimum_amount()
        self.validate_invitation_count()
    
    def approve(self):
        if self.status == 'pending':
            self.status = 'approved'
            self.save()
            # Log the withdrawal transaction
            TransactionHistory.log_transaction(
                user=self.user,
                transaction_type='Withdrawal',
                amount=self.amount,
                description=f"Withdrawal of ${self.amount}"
            )
            
            return True
        return False

    def reject(self):
        if self.status == 'pending':
            wallet = VirtualWallet.objects.get(user=self.user)
            # Refund the amount
            wallet.update_balance(self.amount)  

            # Log the rejected withdrawal transaction
            TransactionHistory.log_transaction(
                user=self.user,
                transaction_type='Withdrawal',
                amount=-self.amount,
                description=f"Rejected withdrawal refund of ${self.amount}"
            )
            self.status = 'rejected'
            self.save()
            return True
        return False

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True,blank=True, db_index=True)


    def __str__(self):
        return self.name
class Tag(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True,blank=True, db_index=True)

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
    slug = models.SlugField(unique=True,blank=True, db_index=True)
    image_url = models.ImageField(blank=True,null=True)


    def __str__(self):
        return f"{self.title} by {self.author.username}"
    @property
    def imgURL(self):
        try:
            url= self.image_url.url
        except:
            url = ''
            return url
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            while Blog.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{''.join(random.choices(string.ascii_letters + string.digits, k=4))}"
            self.slug = slug
        super().save(*args, **kwargs)

class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.blog.title}"
    def get_replies(self):
        return self.replies.all()

class Referral(models.Model):
    inviter = models.ForeignKey(CustomUser, related_name='referrals', on_delete=models.CASCADE)
    invitee = models.OneToOneField(CustomUser, related_name='referral', on_delete=models.CASCADE,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    referral_code = models.CharField(max_length=100, unique=True)
    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        return f'{self.inviter.id}-{self.inviter.username}'

    def get_referral_link(self):
        return f'https://frontearn.onrender.com/?referral={self.referral_code}'
    
    def __str__(self):
        return f"{self.inviter.username} invited {self.invitee.username if self.invitee else 'N/A'}"

class ReferralReward(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - ${self.amount} for {self.reason}"


class ContactFormSubmission(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    subject = models.CharField(max_length=50)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
