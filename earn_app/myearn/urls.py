from django.urls import path
from . import views
urlpatterns = [
    path('register',views.register_user),
    path('customers', views.customer_list, name='customer-list'),\
    path('add-task',views.add_task),
    path('tasks',views.task_list),
    path('complete_task',views.complete_task),

    
]

