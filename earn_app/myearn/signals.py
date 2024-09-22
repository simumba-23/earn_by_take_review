from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task, Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(post_save, sender=Task)
def task_update_handler(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    if created:
        message = f'New task "{instance.name}" has been created.'
    else:
        message = f'Task "{instance.name}" has been updated.'
    
    # Notification.objects.create(user=instance.user, message=message)
    
    async_to_sync(channel_layer.group_send)(
                'global_notifications',
        {
            'type': 'send_notification',
            'message': message
        }
    )
