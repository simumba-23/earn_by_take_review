from rest_framework import serializers
from .models import *

from django.contrib.auth.hashers import make_password
class UserSerializer(serializers.ModelSerializer):
    total_points = serializers.IntegerField()
    class Meta:
        model = CustomUser
        fields = ('id','username','first_name','last_name','email','password','role','phone_number','sex','total_points')
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
class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = '__all__'
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        
# serializers.py
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
        fields = ['id', 'question','selected_option']

class WithdrawalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalRequest
        fields = ['id', 'user', 'amount', 'status', 'created_at', 'updated_at']

class VirtualWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualWallet
        fields = ['user', 'balance']

