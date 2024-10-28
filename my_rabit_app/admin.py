from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(adminmodel)
admin.site.register(CustomerModel)
admin.site.register(WalletModel)
admin.site.register(CallPackageModel)
admin.site.register(UserPurchaseModel)
admin.site.register(WithdrawalHistoryModel)
admin.site.register(AgentTransactionModel)
admin.site.register(PaymentModel)