from rest_framework import serializers
from .models import *


class CustomerSerializer(serializers.ModelSerializer):
    rating = serializers.ReadOnlyField()

    class Meta:
        model = CustomerModel
        fields = '__all__'


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletModel
        fields = '__all__'


class AgentPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPurchaseModel
        fields = '__all__'


class CoinsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallPackageModel
        fields = '__all__'

class WithdrawalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalHistoryModel
        fields = ['agentpurchase_id', 'withdrawal_amount', 'withdrawal_date']


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingModel
        fields = ['rating_id', 'agent', 'user', 'ratings', 'created_at']