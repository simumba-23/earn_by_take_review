from django.contrib import admin
from .models import *

# Register your models here
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('first_name','last_name','email','username','role')
    list_filter = ('username','role')
    search_fields = ('username','email',)

class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'task_type', 'points', 'is_active')
    list_filter = ('task_type', 'is_active')
    search_fields = ('name',)
    
# class UserTaskAdmin(admin.ModelAdmin):
#     list_display = ('user', 'task', 'status', 'completed_at')
#     list_filter = ('status',)
#     search_fields = ('user__username', 'task__name')

# class RewardAdmin(admin.ModelAdmin):
#     list_display = ('user', 'user_task', 'points_earned', 'virtual_money_earned')
#     search_fields = ('user__username',)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'created_at')
    list_filter = ('transaction_type',)
    search_fields = ('user__username',)

# class WithdrawalRequestAdmin(admin.ModelAdmin):
#     list_display = ('user', 'account_details','status', 'amount', 'created_at', 'update_at')
#     list_filter = ('is_approved',)
#     search_fields = ('user__username',)

admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(UserTask)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(WithdrawalRequest)
admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(AnswerOption)



