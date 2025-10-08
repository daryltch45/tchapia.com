def notifications(request):
    """
    Context processor to add notification data to all templates
    """
    context = {}

    if request.user.is_authenticated:
        if request.user.user_type == 'artisan':
            try:
                handyman = request.user.handyman_profile
                # Get unread notifications count
                unread_count = handyman.notifications.filter(is_read=False).count()
                # Get recent notifications (last 5)
                recent_notifications = handyman.notifications.all()[:5]

                context['unread_notifications_count'] = unread_count
                context['recent_notifications'] = recent_notifications
            except:
                context['unread_notifications_count'] = 0
                context['recent_notifications'] = []
        elif request.user.user_type == 'client':
            try:
                customer = request.user.customer_profile
                # Get unread notifications count for customers
                unread_count = customer.notifications.filter(is_read=False).count()
                # Get recent notifications (last 5)
                recent_notifications = customer.notifications.all()[:5]

                context['unread_notifications_count'] = unread_count
                context['recent_notifications'] = recent_notifications
            except:
                context['unread_notifications_count'] = 0
                context['recent_notifications'] = []
        else:
            context['unread_notifications_count'] = 0
            context['recent_notifications'] = []
    else:
        context['unread_notifications_count'] = 0
        context['recent_notifications'] = []

    return context