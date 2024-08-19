from django.urls import path
from . import views
urlpatterns = [
    path('register',views.register_user),
    path('customers', views.customer_list, name='customer-list'),
    path('add-task',views.add_task),
    path('tasks',views.task_list),
    path('tasks/<str:task_type>/', views.task_list),
    path('task/<int:id>/task_detail',views.task_detail),
    path('complete_task',views.complete_task),
    path('surveys/<str:task_id>/task',views.get_survey),
    path('surveys', views.survey_list_create, name='survey-list-create'),
    path('surveys/<int:survey_id>/questions',views.question_list_create, name='question-list-create'),
    path('questions/<int:question_id>/options', views.answer_option_list_create, name='answer-option-list-create'),
    path('submit-answers', views.submit_answers, name='submit-answers'),
    path('surveys/<int:survey_id>/submit',views.submit_answers, name='submit_answers'),
    path('user_tasks_stats',views.user_task_stats),
    path('withdrawal-requests',views.create_withdrawal_request, name='create_withdrawal_request'),
    path('admin_reports',views.admin_reports, name='admin_reports'),
    path('withdrawal-requests/list',views.list_withdrawal_requests, name='list_withdrawal_requests'),
    path('withdrawal-requests/<int:pk>/approve', views.approve_withdrawal_request, name='approve_withdrawal_request'),
    path('withdrawal-requests/<int:pk>/reject', views.reject_withdrawal_request, name='reject_withdrawal_request'),
    path('blogs', views.blog_list, name='blog-list'),
    path('create_blog', views.create_blog),
    path('blogs/<int:pk>/', views.blog_detail, name='blog-detail'),
    path('comments', views.comment_list, name='comment-list'),
    path('comments/<int:pk>/', views.comment_detail, name='comment-detail'),
    path('categories', views.get_categories),
    path('tags', views.get_tags),
    path('spotify-token', views.get_access_token, name='spotify-token')


]


