from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.points.models import UserPoints, PointTransaction
from apps.points.serializers import UserPointsSerializer, PointTransactionSerializer
from common.pagination import StandardPagination


class MyPointsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_points, _ = UserPoints.objects.get_or_create(user=request.user)
        serializer = UserPointsSerializer(user_points)
        return Response(serializer.data)


class MyTransactionsView(generics.ListAPIView):
    serializer_class = PointTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return PointTransaction.objects.filter(user=self.request.user)


class LeaderboardView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        top_users = UserPoints.objects.select_related('user').order_by('-total')[:10]
        data = [{
            'rank': i + 1,
            'username': up.user.username,
            'full_name': up.user.get_full_name(),
            'avatar': up.user.avatar.url if up.user.avatar else None,
            'institution': up.user.institution,
            'total_points': up.total,
        } for i, up in enumerate(top_users)]
        return Response(data)