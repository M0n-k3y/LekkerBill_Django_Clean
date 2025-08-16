from .models import Notification

def notifications_context(request):
    if request.user.is_authenticated:
        unread_notifications = request.user.notifications.filter(is_read=False)
        return {
            'unread_notifications': unread_notifications,
            'unread_notification_count': unread_notifications.count(),
        }
    return {}