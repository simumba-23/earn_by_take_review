from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id','username','first_name','last_name','email','password','role')
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
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        

