from rest_framework import serializers
from .models import *

from django.contrib.auth.hashers import make_password
class UserSerializer(serializers.ModelSerializer):

    ADMIN_REGISTRATION_CODE = 'CARDO_45'
    admin_code = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = CustomUser
        fields = ('id','username','first_name','last_name','email','password','role','phone_number','sex','admin_code')
        extra_kwargs = {
            'password':{'write_only':True},
        }
    def validate(self, data):
        role = data.get('role')
        admin_code = data.get('admin_code')
        if role == 'admin':
            if admin_code != self.ADMIN_REGISTRATION_CODE:
                raise serializers.ValidationError("Invalid admin code")
            data.pop('admin_code', None)

            return data
        
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
        fields = ['id','name','points','media_url','task_type']

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
        # Ensure the request context is provided and retrieve the user
        request = self.context.get('request')
        author = request.user if request else None

        # Create the blog post with the author
        blog = Blog.objects.create(author=author, **validated_data)
        blog.categories.set( categories_data)
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
        fields = ['id', 'question','selected_option']

class WithdrawalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalRequest
        fields = ['id', 'user', 'amount', 'status', 'created_at', 'updated_at']

class VirtualWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualWallet
        fields = ['user', 'balance']

