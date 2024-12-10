from django.db import models
from django.db.models import Avg
# from django.dispatch import receiver
# Create your models here.
class adminmodel(models.Model):
    admin_id=models.AutoField(primary_key=True)
    admin_first_name=models.CharField(max_length=255)
    admin_last_name=models.CharField(max_length=255, blank=True)
    admin_email=models.EmailField()
    admin_password=models.CharField(max_length=255)

    def __str__(self):
        return self.admin_first_name

class CustomerModel(models.Model):
    NORMAL_USER = 'Normal User'
    AGENT_USER = 'Agent User'
    USER_STATUS_CHOICES = [
        (NORMAL_USER, 'Normal User'),
        (AGENT_USER, 'Agent User'),
    ]
    MALE = 'Male'
    FEMALE = 'Female'
    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female')
    ]
    customer_id = models.AutoField(primary_key=True)
    customer_first_name = models.CharField(max_length=100, blank=False)
    customer_last_name = models.CharField(max_length=100, default="unknown")
    customer_email = models.EmailField(default="unknown")
    customer_phone_number = models.CharField(max_length=50)
    customer_password = models.CharField(max_length=100, default='unknown')
    rating = models.IntegerField(default=0)
    terms_conditions = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)
    is_engaged = models.BooleanField(default=False)
    is_existing = models.BooleanField(default=False)
    adhaar_no = models.CharField(max_length=50, default="unknown")
    terms_conditions = models.BooleanField(default=False)
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=USER_STATUS_CHOICES,
        default=NORMAL_USER,
    )

    def __str__(self):
        return f"{self.customer_first_name} {self.customer_last_name} Phone: {self.customer_phone_number}"

    @property
    def rating(self):
        from .models import RatingModel
        rating = RatingModel.objects.filter(agent=self).aggregate(Avg('ratings')).get('ratings__avg')
        return rating if rating is not None else 0

class WalletModel(models.Model):
    wallet_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomerModel, on_delete=models.CASCADE)
    wallet_coins = models.IntegerField(default=300, null=True)
    call_amount = models.FloatField(default=0.0)
    total_minutes = models.IntegerField(default=0)
    total_amount = models.FloatField(default=0.0)

    def __str__(self):
        return f"Wallet of user : {self.user.customer_first_name} {self.user.customer_last_name} Id:- {self.user.customer_id} phone: {self.user.customer_phone_number}"

class CallPackageModel(models.Model):
    coin_id = models.AutoField(primary_key=True)
    package_price = models.FloatField()
    total_coins = models.IntegerField()


class UserPurchaseModel(models.Model):
    # # CHAT = 'Chat'
    # CALL = 'Call'
    # PURCHASE_TYPE_CHOICES = [
    #     (CHAT, 'Chat'),
    #     (CALL, 'Call'),
    # ]
    user_purchase_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomerModel, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField()
    purchase_amount = models.FloatField()
    # purchase_type = models.CharField(max_length=10, choices=PURCHASE_TYPE_CHOICES, null=True)


class WithdrawalHistoryModel(models.Model):
    agentpurchase_id = models.AutoField(primary_key=True)
    agent = models.ForeignKey(CustomerModel, on_delete=models.CASCADE, related_name='withdrawal_requests')
    withdrawal_amount = models.FloatField()
    withdrawal_date = models.DateTimeField(auto_now_add=True)
    withdrawal_method = models.CharField(max_length=20, choices=[
        ('g pay', 'G Pay'),
        ('phone pay', 'Phone Pe'),
        ('bank', 'Bank Transfer'),
    ])
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    bank_account_number = models.CharField(max_length=30, blank=True, null=True)
    bank_ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, default='Pending', choices=[
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Rejected', 'Rejected')
    ])

    def __str__(self):
        return f"Withdrawal by ({self.agent.customer_id} - {self.withdrawal_amount} on {self.withdrawal_date}, {self.status})"

# call details
class CallDetailsModel(models.Model):
    call_id = models.AutoField(primary_key=True)
    caller = models.ForeignKey(CustomerModel, related_name='caller', on_delete=models.CASCADE)
    agent = models.ForeignKey(CustomerModel, related_name='agent', on_delete=models.CASCADE)
    agora_channel_name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(default=0)  # Duration in minutes

class AgentTransactionModel(models.Model):
    # CHAT = 'Chat'
    # CALL = 'Call'
    # TRANSACTION_TYPE_CHOICES = [
    #     (CHAT, 'Chat'),
    #     (CALL, 'Call'),
    # ]
    agent_transaction_id = models.AutoField(primary_key=True)
    agent = models.ForeignKey(CustomerModel, on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomerModel, on_delete=models.CASCADE, related_name='received_transactions',
                                 null=True)
    transaction_amount = models.FloatField()
    transaction_date = models.DateTimeField()
    # transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES, null=True)

    def __str__(self):
        return f"{self.agent.customer_first_name} {self.agent.customer_last_name}"


class PaymentModel(models.Model):
    payment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomerModel, on_delete=models.CASCADE)
    amount = models.FloatField()
    razorpay_id = models.CharField(max_length=100, blank=True)
    # razorpay_payment_signature = models.CharField(max_length=100, blank=True)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.user.customer_first_name} {self.user.customer_last_name}"

class RatingModel(models.Model):
    rating_id = models.AutoField(primary_key = True)
    agent = models.ForeignKey(CustomerModel, on_delete=models.CASCADE, related_name='agent_id')
    user = models.ForeignKey(CustomerModel, on_delete=models.CASCADE, related_name='user')
    ratings = models.IntegerField()
    created_at = models.DateTimeField()