import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status
from .serializers import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from decimal import Decimal
from django.db.models import Sum,Avg,Count,ExpressionWrapper,F,DecimalField,FloatField,Q

logger = logging.getLogger(__name__)


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
@api_view(['GET'])
def task_detail(request,id):
    try:
        task_detail = Task.objects.get(id=id)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
    serializers = TagSerializer(task_detail)
    return Response(serializers.data,status=status.HTTP_200_OK)
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
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_task_stats(request):
    user = request.user
    total_points = UserTask.objects.filter(user=user, status='Completed').aggregate(total_points=models.Sum('points_earned'))['total_points'] or 0
    total_tasks = UserTask.objects.filter(user=user).count()
    completed_tasks = UserTask.objects.filter(user=user, status='Completed').count()
    wallet_balance = VirtualWallet.objects.filter(user=user).aggregate(wallet_balance = models.Sum('balance'))['wallet_balance']
    pending_total = WithdrawalRequest.objects.filter(status='pending').aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    approved_total = WithdrawalRequest.objects.filter(status='approved').aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    return Response({
        "total_points": total_points,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "wallet_balance": wallet_balance,
        "pending_total":pending_total,
        "approved_total":approved_total

    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_reports(request):
    user = request.user
    total_users = CustomUser.objects.filter(role='customer').count()
    active_users_count = CustomUser.objects.filter(usertask__status='Completed').distinct().count()
    users_highest_points = CustomUser.objects.annotate(
    total_points=Sum('usertask__points_earned')
    ).order_by('-total_points')[:10]
    users_highest_points_serialized = UserSerializer(users_highest_points, many=True).data
    # tasks_completed_count = Task.objects.filter(status='completed').count()
    tasks_created_count = Task.objects.count()
    surveys_created_count = Survey.objects.count()
    total_points_earned = Task.objects.aggregate(
    total_points=Sum('points')
    )['total_points']
    average_points_per_task = Task.objects.aggregate(
    average_points=Avg('points')
    )['average_points']

    # popular_task_types = Task.objects.values('task_type').annotate(
    # count=Count('usertasks')
    # ).order_by('-count')
    total_virtual_money_earned = UserTask.objects.aggregate(
    total_money=Sum(ExpressionWrapper(
        F('points_earned') * Decimal(POINTS_TO_MONEY_CONVERSION_RATE),
        output_field=DecimalField()
    ))
    )['total_money']
    total_transactions_count = WithdrawalRequest.objects.count()
    users_with_highest_wallet_balances = VirtualWallet.objects.order_by('-balance')[:10]
    users_with_highest_wallet_balances_serialized = VirtualWalletSerializer(users_with_highest_wallet_balances, many=True).data
    task_completion_rate = UserTask.objects.aggregate(
    completion_rate=ExpressionWrapper(
        Count('id', filter=Q(status='Completed')) * 100.0 / Count('id'),
        output_field=FloatField()
    )
)['completion_rate']

    return Response({
    "total_users": total_users,
    "active_users_count": active_users_count,
    "users_highest_points ":users_highest_points_serialized,
    # "tasks_completed_count" :tasks_completed_count,
    "tasks_created_count" :tasks_created_count,
    "surveys_created_count": surveys_created_count,
    "total_points_earned":total_points_earned,
    "average_points_per_task":average_points_per_task,
    # "popular_task_types ":popular_task_types,
    "total_virtual_money_earned":total_virtual_money_earned,
    "total_transactions_count":total_transactions_count,
    "users_with_highest_wallet_balances":users_with_highest_wallet_balances_serialized,
    "task_completion_rate":task_completion_rate,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_withdrawal_request(request):
    user = request.user
    amount = request.data
    print(amount)

    if amount is None:
        return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        amount = Decimal(amount)
    except (ValueError, TypeError):
        return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        wallet = VirtualWallet.objects.get(user=user)
        if wallet.balance < Decimal('5.00'):
            return Response({'error': 'Balance must be at least $5 to make a withdrawal'}, status=status.HTTP_400_BAD_REQUEST)

        if wallet.balance >= amount:
            wallet.balance -= amount
            wallet.save()
            
            withdrawal_request = WithdrawalRequest.objects.create(
                user=user,
                amount=amount,
                status='pending',
            )
            serializer = WithdrawalRequestSerializer(withdrawal_request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
    except VirtualWallet.DoesNotExist:
        return Response({'error': 'Wallet does not exist'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_withdrawal_requests(request):
    user = request.user
    withdrawal_requests = WithdrawalRequest.objects.all()
    serializer = WithdrawalRequestSerializer(withdrawal_requests, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_withdrawal_request(request, pk):
    try:
        withdrawal_request = WithdrawalRequest.objects.get(pk=pk)
        if withdrawal_request.approve():
            serializer = WithdrawalRequestSerializer(withdrawal_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Insufficient balance or already processed'}, status=status.HTTP_400_BAD_REQUEST)
    except WithdrawalRequest.DoesNotExist:
        return Response({'error': 'Withdrawal request not found'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_withdrawal_request(request, pk):
    try:
        withdrawal_request = WithdrawalRequest.objects.get(pk=pk)
        if withdrawal_request.reject():
            serializer = WithdrawalRequestSerializer(withdrawal_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Already processed'}, status=status.HTTP_400_BAD_REQUEST)
    except WithdrawalRequest.DoesNotExist:
        return Response({'error': 'Withdrawal request not found'}, status=status.HTTP_404_NOT_FOUND)

from rest_framework.pagination import PageNumberPagination   
@api_view(['GET'])
def blog_list(request):
    # Initialize the pagination class
    paginator = PageNumberPagination()
    paginator.page_size = 10  # Number of items per page, adjust as needed

    # Get the blogs and paginate them
    blogs = Blog.objects.all()
    paginated_blogs = paginator.paginate_queryset(blogs, request)
    serializer = BlogSerializer(paginated_blogs, many=True)
    
    # Return paginated response
    return paginator.get_paginated_response(serializer.data)   
 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_blog(request):
    author = request.user.id
    print("author:",author)
    serializer = BlogSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def blog_detail(request, pk):
    try:
        blog = Blog.objects.get(pk=pk)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BlogSerializer(blog)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = BlogSerializer(blog, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        blog.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def comment_list(request):
    if request.method == 'GET':
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def comment_detail(request, pk):
    try:
        comment = Comment.objects.get(pk=pk)
    except Comment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def get_categories(request):
    categories_list = Category.objects.all()
    serializers = CategorySerializer(categories_list,many=True)
    return Response(serializers.data,status=status.HTTP_200_OK)

@api_view(['GET'])
def get_tags(request):
    tag_list = Tag.objects.all()
    serializers = TagSerializer(tag_list,many=True)
    return Response(serializers.data,status=status.HTTP_200_OK)

    

