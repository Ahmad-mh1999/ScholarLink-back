from .models import UserPoints, PointTransaction

POINTS = {
    'publish_article': 10,
    'receive_like': 2,
    'submit_review': 5,
    'receive_comment': 1,
    'receive_bookmark': 3,
}


def award_points(user, reason):
    points_value = POINTS.get(reason, 0)
    if points_value == 0:
        return

    user_points, _ = UserPoints.objects.get_or_create(user=user)
    user_points.total += points_value
    user_points.save()

    PointTransaction.objects.create(
        user=user,
        points=points_value,
        reason=reason
    )
    return user_points.total