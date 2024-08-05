from django.urls import path
from . import views
urlpatterns = [
    path('register',views.register_user),
    path('customers', views.customer_list, name='customer-list'),
    path('add-task',views.add_task),
    path('tasks',views.task_list),
    path('tasks/<str:task_type>/', views.task_list),
    path('complete_task',views.complete_task),
    path('surveys/<str:task_id>/task',views.get_survey),
    path('surveys', views.survey_list_create, name='survey-list-create'),
    path('surveys/<int:survey_id>/questions',views.question_list_create, name='question-list-create'),
    path('questions/<int:question_id>/options', views.answer_option_list_create, name='answer-option-list-create'),
    path('submit-answers', views.submit_answers, name='submit-answers'),
    path('surveys/<int:survey_id>/submit',views.submit_answers, name='submit_answers'),


    
]

