import os
import firebase_admin
from firebase_admin import credentials,messaging

cred = credentials.Certificate('earn_app\\serviceAccountKey.json')
firebase_admin.initialize_app(cred)

def send_notification(user ,title, body,token =None, data=None): 
    try:
        if not token:
            from .models import DiviceToken
            # Fetch the device token for a specific user
            device = DiviceToken.objects.get(user=user)
            token = device.token
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,
            data=data if data else {},
        )
        response = messaging.send(message)
        return {"success": f"Notification sent: {response}"}
    except Exception as e:
        return {"error": str(e)}
