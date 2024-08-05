from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status
from .serializers import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import *
from datetime import timezone
from rest_framework_simplejwt.views import TokenObtainPairView

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username 
        token['role'] = user.role  

        return token



class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

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
@api_view(['GET'])
def get_survey(request, task_id):
    try:
        survey = Survey.objects.get(task_id=task_id)
    except Survey.DoesNotExist:
        return Response({'error': 'Survey not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = SurveySerializer(survey)
    return Response(serializer.data)

@api_view(['POST'])
def complete_task(request):
    task_id = request.data.get('taskId')
    answers_data = request.data.get('answers')
    user_task = UserTask.objects.get(user=request.user, task__id=task_id)
    if user_task.is_completed:
        return Response({'error': 'Task already completed'}, status=status.HTTP_400_BAD_REQUEST)
    
    for answer_data in answers_data:
        question_id = answer_data.get('question_id')
        selected_option_id = answer_data.get('selected_option_id')
        Answer.objects.create(
            question_id=question_id,
            user_task=user_task,
            selected_option_id=selected_option_id
        )
    
    user_task.is_completed = True
    user_task.save()
    
    return Response({'success': 'Task completed successfully'})
@api_view(['GET', 'POST'])
def survey_list_create(request):
    if request.method == 'GET':
        surveys = Survey.objects.all()
        serializer = SurveySerializer(surveys, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = SurveySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def question_list_create(request, survey_id):
    if request.method == 'GET':
        questions = Question.objects.filter(survey_id=survey_id)
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def answer_option_list_create(request, question_id):
    if request.method == 'GET':
        options = AnswerOption.objects.filter(question_id=question_id)
        serializer = AnswerOptionSerializer(options, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = AnswerOptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_answers(request, survey_id):
    user = request.user
    answers = request.data

    try:
        survey = Survey.objects.get(id=survey_id)
        points_to_add = survey.task.points
        
        # Create a new UserTask if it doesn't exist
        user_task, created = UserTask.objects.get_or_create(
            user=user,
            task=survey.task,
            defaults={'points_earned': 0}
        )

        for answer in answers:
            question = Question.objects.get(id=answer['question'])
            selected_option = AnswerOption.objects.get(id=answer['selected_option'])
            Answer.objects.create(
                user_task=user_task,
                question=question,
                selected_option=selected_option,
            )

        user_task.status = 'completed'
        user_task.points_earned += points_to_add
        user_task.save()
        return Response({'message': 'Answers submitted successfully and points updated!'}, status=status.HTTP_201_CREATED)
    except (Survey.DoesNotExist, Question.DoesNotExist, AnswerOption.DoesNotExist) as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)