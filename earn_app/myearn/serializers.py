from rest_framework import serializers
from .models import *

from django.contrib.auth.hashers import make_password
class UserSerializer(serializers.ModelSerializer):
    total_points_earned = serializers.SerializerMethodField()
    referral_status = serializers.SerializerMethodField()
    ADMIN_REGISTRATION_CODE = 'CARDO_45'
    class Meta:
        model = CustomUser
        fields = ('id','username','first_name','last_name','email','password','role','phone_number','sex','is_active','is_banned','total_points_earned','referral_status','date_joined')
        extra_kwargs = {
            'password':{'write_only':True},
        }
    
    def create(self, validated_data):
        # Extract the password from validated data
        password = validated_data.pop('password', None)
        # Create the user instance
        user = super().create(validated_data)
        # Set the password
        if password:
            user.password = make_password(password)
            user.save()
        return user
    def get_total_points_earned(self, obj):
        return UserTask.objects.filter(user=obj).aggregate(total_points=models.Sum('points_earned'))['total_points'] or 0
    def get_referral_status(self, obj):
        referrals_count = Referral.objects.filter(inviter=obj).count()
        return f"{referrals_count}"
class BulkActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['suspend', 'delete', 'ban', 'unban'])
    user_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)
    
class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = '__all__'
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id','name','points','media_url','task_type']
class UserTaskSerializer(serializers.ModelSerializer):
    task = TaskSerializer()

    class Meta:
        model = UserTask
        fields = ['id', 'user', 'task', 'status', 'points_earned', 'created_at']

    def get_progress(self, obj):
        total_tasks = Task.objects.count()
        completed_tasks = UserTask.objects.filter(user=obj.user, status='Completed').count()
        return (completed_tasks / total_tasks) * 100

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
    def validate_slug(self, value):
        if Category.objects.filter(slug=value).exists():
            raise serializers.ValidationError("A category with this slug already exists.")
        return value

    def create(self, validated_data):
        if 'slug' not in validated_data or not validated_data['slug']:
            validated_data['slug'] = self.generate_unique_slug(validated_data['name'])
        return super().create(validated_data)

    def generate_unique_slug(self, name):
        import uuid
        slug = name.lower().replace(' ', '-')
        while Category.objects.filter(slug=slug).exists():
            slug = f"{slug}-{uuid.uuid4().hex[:8]}"
        return slug

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
    def validate_slug(self, value):
        if Tag.objects.filter(slug=value).exists():
            raise serializers.ValidationError("A Tag with this slug already exists.")
        return value

    def create(self, validated_data):
        if 'slug' not in validated_data or not validated_data['slug']:
            validated_data['slug'] = self.generate_unique_slug(validated_data['name'])
        return super().create(validated_data)

    def generate_unique_slug(self, name):
        import uuid
        slug = name.lower().replace(' ', '-')
        while Tag.objects.filter(slug=slug).exists():
            slug = f"{slug}-{uuid.uuid4().hex[:8]}"
        return slug

    

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
class BlogSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Blog
        fields = '__all__'

    def create(self, validated_data):
        categories_data = validated_data.pop('categories')
        tags_data = validated_data.pop('tags')
        request = self.context.get('request')
        author = request.user if request else None

        blog = Blog.objects.create(author=author, **validated_data)
        blog.categories.set(categories_data)
        blog.tags.set(tags_data)
        return blog

    def update(self, instance, validated_data):
        categories_data = validated_data.pop('categories', None)
        tags_data = validated_data.pop('tags', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if categories_data is not None:
            instance.categories.set(categories_data)
        if tags_data is not None:
            instance.tags.set(tags_data)

        instance.save()
        return instance
    
class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ['id', 'task', 'title']

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'survey', 'text', 'is_multiple_choice']

class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = ['id', 'question', 'text']

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id','question','selected_option']

class WithdrawalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalRequest
        fields = ['id', 'user', 'amount', 'status', 'created_at', 'updated_at']

class VirtualWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualWallet
        fields = ['user', 'balance']
class InviteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'date_joined']  # Include any other relevant fields

class ReferralSerializer(serializers.ModelSerializer):
    invitees_count = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Referral
        fields = ['inviter','invitee','created_at', 'referral_code','invitees_count','status']
    def get_invitees_count(self, obj):
        return Referral.objects.filter(inviter=obj.inviter).count()
    def get_status(self, obj):
        referrals_count = Referral.objects.filter(inviter=obj.inviter).count()
        return f"{referrals_count}" 

class ReferralRewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralReward
        fields = ['created_at', 'amount', 'reason']


class ContactFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactFormSubmission
        fields = ['user', 'name', 'email', 'phone_number', 'subject', 'message']
        read_only_fields = ['user']  

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords do not match")
        return data

    def validate_old_password(self, old_password):
        user = self.context['request'].user
        if not user.check_password(old_password):
            raise serializers.ValidationError("Old password is incorrect")
        return old_password

class Generate2FASerializer(serializers.Serializer):
    otp_url = serializers.CharField()

class Verify2FASerializer(serializers.Serializer):
    otp_code = serializers.CharField()

class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = ['id','transaction_type','amount', 'description', 'created_at']

class EarningHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EarningHistory
        fields = ['id', 'user_task', 'points_earned', 'money_earned', 'created_at']

class VisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visit
        fields = '__all__'

class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = '__all__'

class RewardClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardClaim
        fields = '__all__'