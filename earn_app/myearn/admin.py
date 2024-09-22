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

# class WithdrawalRequestAdmin(admin.ModelAdmin):
#     list_display = ('user', 'account_details','status', 'amount', 'created_at', 'update_at')
#     list_filter = ('is_approved',)
#     search_fields = ('user__username',)
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'author', 'created_at', 'updated_at')
    search_fields = ('title', 'content')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('blog', 'author', 'created_at')
    search_fields = ('content',)
@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('inviter', 'invitee', 'created_at')
    search_fields = ('inviter__username', 'invitee__username')

@admin.register(ReferralReward)
class ReferralRewardAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'reason', 'created_at')
    search_fields = ('user__username',)
    
admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(UserTask)
admin.site.register(WithdrawalRequest)
admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(AnswerOption)
admin.site.register(VirtualWallet)
admin.site.register(EarningHistory)
admin.site.register(TransactionHistory)





