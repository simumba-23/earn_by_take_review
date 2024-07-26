from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status
from .serializers import UserSerializer,TaskSerializer
from .models import *
from datetime import timezone


@api_view(['POST'])
def register_user(request):
    print("request Data",request.data)
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user=serializer.save()
        print(f'User {user.username} registered with role {user.role}')
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
@api_view(['GET'])
def customer_list(request):
    customers = CustomUser.objects.filter(role='customer')
    serializer = UserSerializer(customers, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def task_list(request, task_type=None):
    if task_type:
        tasks = Task.objects.filter(task_type=task_type, is_active=True)
    else:
        tasks = Task.objects.filter(is_active=True)
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def add_task(request):
    if request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
def complete_task(request):
    task_id = request.data.get('taskId')
    user = request.user

    try:
        task = Task.objects.get(id=task_id)
        
        # Create or update the UserTask entry
        user_task, created = UserTask.objects.get_or_create(
            user=user,
            task=task,
            defaults={'status': 'completed', 'completed_at': timezone.now()}
        )
        
        if not created:
            user_task.status = 'completed'
            user_task.completed_at = timezone.now()
            user_task.save()
        
        # Calculate new totals
        new_points = user.total_points + task.points
        new_virtual_money = user.total_virtual_money + task.virtual_money
        
        # Update user's total points and virtual money
        user.total_points = new_points
        user.total_virtual_money = new_virtual_money
        user.save()

        # Create a Reward entry
        reward, reward_created = Reward.objects.get_or_create(
            user=user,
            user_task=user_task,
            defaults={
                'points_earned': task.points,
                'virtual_money_earned': task.virtual_money
            }
        )
        
        if not reward_created:
            reward.points_earned = task.points
            reward.virtual_money_earned = task.virtual_money
            reward.save()

        return Response({'status': 'Task completed and reward added', 'total_points': new_points, 'total_virtual_money': new_virtual_money}, status=200)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=404)





