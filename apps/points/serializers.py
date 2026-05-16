from rest_framework import serializers
from .models import UserPoints, PointTransaction
from apps.accounts.serializers import UserSerializer


class PointTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointTransaction
        fields = ['id', 'points', 'reason', 'created_at']


class UserPointsSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    transactions = PointTransactionSerializer(
        source='user.transactions',
        many=True,
        read_only=True
    )

    class Meta:
        model = UserPoints
        fields = ['user', 'total', 'transactions', 'updated_at']