from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render


def is_admin(user):
    return getattr(user, 'role', None) == 'admin' or getattr(user, 'is_staff', False)


@user_passes_test(is_admin)
def admin_send_notification_view(request):
    return render(request, 'admin/notifications/send.html')

