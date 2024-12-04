from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponse, HttpResponseRedirect
from .forms import *
from django.views.decorators.http import require_POST, require_GET
from datetime import datetime
from django.db.models import Q, Sum
from django.utils.dateparse import parse_date
from .models import *
from .serializer import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

# Create your views here.
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            admin = adminmodel.objects.get(admin_email=email, admin_password=password)
            admin_name = f"{admin.admin_first_name} {admin.admin_last_name}"
            request.session['user'] = admin_name
            request.session.set_expiry(21600)

            expiry = request.session.get_expiry_age()

            return redirect('home')
        except adminmodel.DoesNotExist:
            return render(request, 'login.html', {'error': "User not found"})
    return render(request, 'login.html')


# def reg(request):
#     if request.method == 'POST':
#         form = AdminForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('login')  # Redirect to login page after successful registration
#     else:
#         form = AdminForm()
#     return render(request, 'register.html', {'form': form})


def home(request):
    username = request.session.get('user', None)
    if username is None:
        return redirect('/login')
    else:
        normal_users_count = CustomerModel.objects.filter(status='Normal User').count
        agent_user_count = CustomerModel.objects.filter(status='Agent User').count
        all_agents = CustomerModel.objects.filter(status='Agent User')
        payments = PaymentModel.objects.all().aggregate(Sum('amount'))
        amount = payments['amount__sum']
        # Ensure each agent's rating is included in the context
        agents_with_ratings = []
        for agent in all_agents:
            agent_rating = agent.rating  # This uses the rating property defined in the model
            agents_with_ratings.append({
                'customer_first_name': agent.customer_first_name,
                'customer_last_name': agent.customer_last_name,
                'customer_id': agent.customer_id,
                # 'is_online': agent.is_online,
                'rating': agent_rating
            })

        # Total Revenue from Users
        total_revenue = UserPurchaseModel.objects.aggregate(Sum('purchase_amount'))['purchase_amount__sum']

        # Total Payments to Agents (For Chats and Calls)
        total_agent_payments = AgentTransactionModel.objects.aggregate(Sum('transaction_amount'))[
            'transaction_amount__sum']

        # Total Withdrawals by Agents
        total_withdrawals = WithdrawalHistoryModel.objects.aggregate(Sum('withdrawal_amount'))['withdrawal_amount__sum']

        total_agent_payments = total_agent_payments or 0
        total_withdrawals = total_withdrawals or 0

        # Calculating Profit
        company_profit = total_revenue - (total_agent_payments + total_withdrawals)
        if total_revenue:
            profit = round((company_profit / total_revenue) * 100, 2)
        else:
            profit = 0.00
    return render(request, 'index.html', {'normaluser': normal_users_count, 'agentuser': agent_user_count,
                                          'all_agents': agents_with_ratings, 'payments': amount, 'username': username,
                                          'profit': profit})


def registered_users(request):
    username = request.session.get('user', None)
    if username is None:
        return redirect('/login')
    else:
        users = CustomerModel.objects.all()
        if request.method == 'POST':
            # Handle status update
            userid = request.POST.get('user_id')

            # Handle status update if present
            if 'status' in request.POST:
                new_status = request.POST.get('status')
                user = CustomerModel.objects.get(customer_id=userid)
                if new_status != user.status:  # Update only if status has changed
                    user.status = new_status
                    user.save()

                    # Update wallet based on user status
                    wallet = WalletModel.objects.get(user=userid)
                    if new_status == 'Normal User':
                        wallet.wallet_coins = 300
                        # wallet.purchase_date = None
                        wallet.agent_balance = 0
                        wallet.save()
                    elif new_status == 'Agent User':
                        wallet.wallet_coins = 0
                        # wallet.purchase_date = None
                        wallet.save()

                        user.is_existing = False
                        user.save()
    return render(request, 'registered_users.html', {'users': users})


def delete_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id:
            try:
                user = CustomerModel.objects.get(pk=user_id)
                user.delete()
                return redirect('users')  # Redirect to the users list page after deletion
            except CustomerModel.DoesNotExist:
                return redirect('users')  # Handle the case where the user does not exist
    return HttpResponseNotAllowed(['POST'])


def add_user(request):
    username = request.session.get('user', None)
    if username is None:
        return redirect('/login')
    else:
        if request.method == 'POST':
            form = CustomerForm(request.POST)
            if form.is_valid():
                customer = form.save()  # Saves the form data to the CustomerModel database table

                wallet = WalletModel(user=customer)
                wallet.save()

                return redirect('users')  # Redirect to a success page or another view after successful submission
        else:
            form = CustomerForm()
    return render(request, 'add_user.html', {'form': form, 'username': username})


def delete_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id:
            try:
                user = CustomerModel.objects.get(pk=user_id)
                user.delete()
                return redirect('users')  # Redirect to the users list page after deletion
            except CustomerModel.DoesNotExist:
                return redirect('users')  # Handle the case where the user does not exist
    return HttpResponseNotAllowed(['POST'])


def normal_user(request):
    username = request.session.get('user', None)
    if username is None:
        return redirect('/login')
    users = CustomerModel.objects.filter(status='Normal User')
    return render(request, 'normaluser.html', {'users': users, 'username': username})


def wallet_normaluser(request):
    username = request.session.get('user', None)
    if username is None:
        return redirect('/login')
    wallets = WalletModel.objects.filter(user__status='Normal User')
    return render(request, 'normaluser_wallet.html', {'wallets': wallets, 'username': username})


def agent_user(request):
    username = request.session.get('user', None)
    if username is None:
        return redirect('/login')
    users = CustomerModel.objects.filter(status='Agent User')
    return render(request, 'agentuser.html', {'users': users, 'username': username})


def wallet_agentuser(request):
    username = request.session.get('user', None)
    if username is None:
        return redirect('/login')

    wallets = WalletModel.objects.filter(user__status='Agent User')
    return render(request, 'agentuser_wallet.html', {'wallets': wallets, 'username': username})


def coin_package(request):
    username = request.session.get('user', None)
    if username is None:
        return redirect('/login')
    coins = CallPackageModel.objects.all()
    return render(request, 'coin_package.html', {'coins': coins, 'username': username})


def logout(request):
    del request.session['user']
    return redirect('login')


@require_POST
def delete_coin_package(request, coin_id):
    coin_package = get_object_or_404(CallPackageModel, coin_id=coin_id)
    coin_package.delete()
    return redirect('coin_package')


def add_package(request):
    username = request.session.get('user', None)
    if username is None:
        return redirect('/login')
    else:
        if request.method == 'POST':
            callform = CallPackageForm(request.POST)

            if request.POST.get('call_package'):
                if callform.is_valid():
                    callform.save()
                    return redirect('coin_package')

        else:
            callform = CallPackageForm()
    return render(request, 'add_package.html', {'callform': callform, 'username': username})


def user_history(request):
    username = request.session.get('user', None)
    if username is None:
        return redirect('/login')

    user_history = UserPurchaseModel.objects.all()
    return render(request, 'normaluser_history.html', {'user_history': user_history, 'username': username})


def agent_history(request):
    username = request.session.get('user', None)
    if username is None:
        return redirect('/login')

    agent_history = WithdrawalHistoryModel.objects.all()
    return render(request, 'agentuser_history.html', {'agent_history': agent_history, 'username': username})

@csrf_exempt
def update_withdrawal_status(request, history_id):
    if request.method == 'POST':
        new_status = request.POST.get('status')
        try:
            history = WithdrawalHistoryModel.objects.get(pk=history_id)
            history.status = new_status
            history.save()
            return JsonResponse({'success': True})
        except WithdrawalHistoryModel.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Record not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


# Search Bar View
def search_results(request):
    query = request.GET.get('q')
    results = None
    if query:
        results = CustomerModel.objects.filter(
            Q(customer_first_name__icontains=query) |  # Search by first name
            Q(customer_last_name__icontains=query) |  # Search by last name
            Q(customer_phone_number__icontains=query) |  # Search by phone number
            Q(Q(customer_first_name__icontains=query.split()[0]) & Q(customer_last_name__icontains=query.split()[-1]))
            # Search by full name
        )

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'search_results.html', context)


def agent_search(request):
    first_name = request.GET.get('first_name', '')
    last_name = request.GET.get('last_name', '')
    phone_number = request.GET.get('phone_number', '')

    # Filter by fields if provided
    results = CustomerModel.objects.filter(status='Agent User')

    if first_name:
        results = results.filter(customer_first_name__icontains=first_name)
    if last_name:
        results = results.filter(customer_last_name__icontains=last_name)
    if phone_number:
        results = results.filter(customer_phone_number__icontains=phone_number)

    return render(request, 'search_results.html', {'results': results})


def user_search(request):
    first_name = request.GET.get('first_name', '')
    last_name = request.GET.get('last_name', '')
    phone_number = request.GET.get('phone_number', '')

    # Filter by fields if provided
    results = CustomerModel.objects.filter(status='Normal User')

    if first_name:
        results = results.filter(customer_first_name__icontains=first_name)
    if last_name:
        results = results.filter(customer_last_name__icontains=last_name)
    if phone_number:
        results = results.filter(customer_phone_number__icontains=phone_number)

    return render(request, 'search_results.html', {'results': results})


def agent_report(request):
    agents = CustomerModel.objects.filter(status='Agent User')
    report_data = {}
    if request.method == 'POST':
        agent_id = request.POST.get('agent_id')
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')

        from_date = parse_date(from_date) if from_date else None
        to_date = parse_date(to_date) if to_date else None

        if not agent_id or not from_date or not to_date:
            return JsonResponse({'error': 'Agent, from date, and to date are required'}, status=400)

        agent = get_object_or_404(CustomerModel, customer_id=agent_id)
        wallet = WalletModel.objects.get(user__customer_id=agent_id)
        withdrawals = WithdrawalHistoryModel.objects.filter(agent=agent, withdrawal_date__range=[from_date, to_date])
        transactions = AgentTransactionModel.objects.filter(agent=agent, transaction_date__range=[from_date, to_date])
        wallet_data = {
            'call_amount': wallet.call_amount if wallet else 0,
            'total_minutes': wallet.total_minutes if wallet else 0,
            'total_amount': wallet.total_amount if wallet else 0,
        }
        withdrawal_data = [
            {
                'withdrawal_amount': w.withdrawal_amount,
                'withdrawal_date': w.withdrawal_date.strftime('%d %B %Y %I:%M %p')
            }
            for w in withdrawals
        ]
        transactions_data = [
            {
                "receiver": f"{t.receiver.customer_first_name} {t.receiver.customer_last_name}",
                "amount": t.transaction_amount,
                "date": t.transaction_date.strftime('%d %B %Y %I:%M %p'),
                # "type": t.transaction_type
            }
            for t in transactions
        ]
        report_data = {
            'agent_name': f"{agent.customer_first_name} {agent.customer_last_name}",
            'wallet': wallet_data,
            'transactions': transactions_data,
            'withdrawals': withdrawal_data,
        }
        return JsonResponse(report_data, status=200)
    return render(request, 'agent_report.html', {'agents': agents})


# def user_report(request):
#     users = CustomerModel.objects.filter(status='Normal User')
#     report_data = {}
#     if request.method == 'POST':
#         user_id = request.POST.get('agent_id')
#         from_date = request.POST.get('from_date')
#         to_date = request.POST.get('to_date')
#
#         from_date = parse_date(from_date) if from_date else None
#         to_date = parse_date(to_date) if to_date else None
#
#         if not user_id or not from_date or not to_date:
#             return JsonResponse({'error': 'Agent, from date, and to date are required'}, status=400)
#
#         user = get_object_or_404(CustomerModel, customer_id=user_id)
#         wallet = WalletModel.objects.get(user__customer_id=user_id)
#         purchases =  UserPurchaseModel.objects.filter(user=user, purchase_date__range=[from_date, to_date])
#         transactions = AgentTransactionModel.objects.filter(user=user, transaction_date__range=[from_date, to_date])
#         wallet_data = {
#             'call_amount': wallet.call_amount if wallet else 0,
#             # 'chat_amount': wallet.chat_amount if wallet else 0,
#             # 'total_messages_received': wallet.total_messages_received if wallet else 0,
#             'total_minutes': wallet.total_minutes if wallet else 0,
#             'total_amount': wallet.total_amount if wallet else 0,
#         }
#         withdrawal_data = [
#             {
#                 'purchase_amount': p.purchase_amount,
#                 'purchase_date': p.purchase_date.strftime('%d %B %Y %I:%M %p')
#             }
#             for p in purchases
#         ]
#         transactions_data = [
#             {
#                 "receiver": f"{t.receiver.customer_first_name} {t.receiver.customer_last_name}",
#                 "amount": t.transaction_amount,
#                 "date": t.transaction_date.strftime('%d %B %Y %I:%M %p'),
#                 # "type": t.transaction_type
#             }
#             for t in transactions
#         ]
#         report_data = {
#             'agent_name': f"{user.customer_first_name} {user.customer_last_name}",
#             'wallet': wallet_data,
#             'transactions': transactions_data,
#             'withdrawals': withdrawal_data,
#         }
#         return JsonResponse(report_data, status=200)
#     return render(request, 'agent_report.html', {'users': users})


def report_view(request):
    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        if from_date and to_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d')
            to_date = datetime.strptime(to_date, '%Y-%m-%d')

            user_details = []
            agent_details = []

            users = CustomerModel.objects.filter(status='Normal User')

            for user in users:
                purchases = UserPurchaseModel.objects.filter(user=user, purchase_date__range=[from_date, to_date])
                payments = PaymentModel.objects.filter(user=user, created_at__range=[from_date, to_date])
                user_details.append({
                    'user': {
                        'first_name': user.customer_first_name if user else None,
                        'last_name': user.customer_last_name if user else None,
                        'email': user.customer_email if user else None,
                        'contact': user.customer_phone_number,
                    },
                    'purchases': [
                        {
                            'purchase_date': '-' if not purchases else purchase.purchase_date.strftime(
                                '%d %B %Y %I:%M %p'),
                            'purchase_amount': '-' if not purchases else purchase.purchase_amount,
                        }
                        for purchase in purchases
                    ],
                    'payments': [
                        {
                            'created_at': '-' if not payments else payment.created_at.strftime('%d %B %Y %I:%M %p'),
                            'amount': '-' if not payments else payment.amount
                        }
                        for payment in payments
                    ],
                })

            agents = CustomerModel.objects.filter(status='Agent User')

            for agent in agents:
                withdrawals = WithdrawalHistoryModel.objects.filter(agent=agent,
                                                                    withdrawal_date__range=[from_date, to_date])
                transactions = AgentTransactionModel.objects.filter(agent=agent,
                                                                    transaction_date__range=[from_date, to_date])
                agent_details.append({
                    'agent': {
                        'customer_id': agent.customer_id,
                        'first_name': agent.customer_first_name,
                        'last_name': agent.customer_last_name,
                        'email': agent.customer_email,
                        'contact': agent.customer_phone_number,
                        'status': agent.status,
                    },
                    'withdrawals': [
                        {
                            'withdrawal_date': withdrawal.withdrawal_date.strftime('%d %B %Y %I:%M %p'),
                            'withdrawal_amount': withdrawal.withdrawal_amount
                        }
                        for withdrawal in withdrawals
                    ],
                    'transactions': [
                        {
                            'transaction_date': transaction.transaction_date.strftime('%d %B %Y %I:%M %p'),
                            'transaction_amount': transaction.transaction_amount,
                        }
                        for transaction in transactions
                    ],
                })
            return JsonResponse({'user_details': user_details, 'agent_details': agent_details})

        return JsonResponse({'error': 'Invalid date range'}, status=400)

    return render(request, 'report.html')


@require_GET
def get_payment_data(request):
    # Fetching payments data
    payments = PaymentModel.objects.all()

    # Aggregating data by month
    data = {}
    for payment in payments:
        month = payment.created_at.strftime("%b")  # Get the month abbreviation (e.g., 'Jan')
        if month not in data:
            data[month] = 0
        data[month] += float(payment.amount)

    # Making sure all months are present in the data, even if they have 0 earnings
    all_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    data = {month: data.get(month, 0) for month in all_months}

    # Sorting data by month
    sorted_data = {month: data[month] for month in all_months}

    return JsonResponse(sorted_data)




#  View for API  ################################################################################################################################

@api_view(['GET'])
def check_users(request, mobileno):
    # Check if the user already exists
    try:
        user = CustomerModel.objects.get(customer_phone_number=mobileno)
        user_data = CustomerSerializer(user)
        return Response(user_data.data, status=status.HTTP_200_OK)

    except CustomerModel.DoesNotExist:
        return Response({'message': 'User not existing'}, status=400)

@api_view(['POST'])
def customers(request):
    contact = request.data.get('mobile_no')
    # password = request.data.get('password')
    gender = request.data.get('gender')
    if not contact:
        return Response({'error': 'Phone Number required'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate if the contact number contains only digits and is exactly 10 digits long
    if not contact.isdigit() or len(contact) != 10:
        return Response(
            {'error': 'Invalid Phone Number. It must be exactly 10 digits long and contain only numbers.'},
            status=status.HTTP_400_BAD_REQUEST)

    # Check if the user already exists
    try:
        user = CustomerModel.objects.get(customer_phone_number=contact)
        # If the user exists, check if the password is correct
        # if user.customer_password != password:
        #     return Response({'error': 'Incorrect password'}, status=status.HTTP_400_BAD_REQUEST)

        # If the password is correct, update user's is_existing and is_online to True
        user.is_existing = True
        user.is_online = True
        user.save()
        user_data = CustomerSerializer(user)
        return Response(user_data.data, status=status.HTTP_200_OK)

    except CustomerModel.DoesNotExist:
        # Validate the password using check_password function
        # is_valid, error_message = check_password(password)
        # if not is_valid:
        #     return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

        # If user does not exist, create a new user
        user = CustomerModel.objects.create(
            customer_phone_number=contact,
            # customer_password=password,
            gender=gender,
            is_existing=False,
            is_online=True
        )
        user.save()

        # Create a wallet for the new user
        wallet = WalletModel(user=user)
        wallet.save()

    user_data = CustomerSerializer(user)
    return Response(user_data.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def all_users(request):
    users = CustomerModel.objects.filter(status=CustomerModel.NORMAL_USER)
    user_data = []

    for user in users:
        user_data.append({
            'customer_id': user.customer_id,
            'customer_first_name': user.customer_first_name,
            'customer_last_name': user.customer_last_name,
            'customer_contact': user.customer_phone_number,
            'customer_password': user.customer_password,
            'gender': user.gender,
            'status': user.status,
            'is_online': user.is_online,
            'rating': user.rating
        })

    return Response(user_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def all_agents(request):
    users = CustomerModel.objects.filter(status=CustomerModel.AGENT_USER)
    user_data = []

    for user in users:
        user_data.append({
            'customer_id': user.customer_id,
            'customer_first_name': user.customer_first_name,
            'customer_last_name': user.customer_last_name,
            'customer_contact': user.customer_phone_number,
            'customer_password': user.customer_password,
            'gender': user.gender,
            'status': user.status,
            'is_online': user.is_online,
            'rating':user.rating
        })

    return Response(user_data, status=status.HTTP_200_OK)

@api_view(['POST'])
def update_profile(request, id):
    user = CustomerModel.objects.get(customer_id=id)
    user_data = CustomerSerializer(instance=user, data=request.data, partial=True)
    if user_data.is_valid():
        user_data.save()
        return Response({"message": "Profile updated successfully"})
    return Response(user_data.errors)

@api_view(['GET'])
def wallet(request, id):
    wallet = WalletModel.objects.get(user=id)
    wallet_data = WalletSerializer(wallet, many=False)
    return Response(wallet_data.data)

@api_view(['POST'])
def withdrawal(request, id):
    agent = WalletModel.objects.get(user__customer_id=id)
    agent_amount = float(request.data.get('amount'))
    withdrawal_method = request.data.get('withdrawal_method')
    payment_details = request.data.get('payment_details')
    print("Agent's total amount:", agent.total_amount)
    print("Requested withdrawal amount:", agent_amount)

    if agent.total_amount >= 5000:
        agent.total_amount = agent.total_amount - agent_amount
        agent.save()
        withdrawal = WithdrawalHistoryModel.objects.create(
            agent=CustomerModel.objects.get(customer_id=id),
            withdrawal_amount=agent_amount,
            withdrawal_date=datetime.now(),
            withdrawal_method=withdrawal_method,
            status = 'Pending'
        )
        # Create a withdrawal history entry
        if withdrawal_method in ['gpay', 'phonepay']:
            withdrawal.phone_number = payment_details.get('phone_number')
        elif withdrawal_method == 'bank':
            withdrawal.bank_account_number = payment_details.get('account_number')
            withdrawal.bank_ifsc_code = payment_details.get('ifsc_code')
        withdrawal.save()

        return JsonResponse({'message': f'Withdrawn amount: {agent_amount}'}, status=200)
    else:
        # Return error response if balance is insufficient
        return JsonResponse({'error': 'Insufficient balance for withdrawal'}, status=400)

@api_view(['POST'])
def start_call(request):
    caller_id = request.data.get('caller_id')
    agent_id = request.data.get('agent_id')
    agora_channel_name = request.data.get('agora_channel_name')

    # Check if caller has enough coins to start the call (at least 150 coins)
    caller_wallet = WalletModel.objects.get(user_id=caller_id)
    if caller_wallet.wallet_coins < 150:
        return Response({"error": "Insufficient coins to start the call"}, status=400)

    call = CallDetailsModel.objects.create(
        caller_id=caller_id,
        agent_id=agent_id,
        agora_channel_name=agora_channel_name,
        start_time=timezone.now()
    )

    agent = CustomerModel.objects.get(customer_id=agent_id)
    agent.is_online = False
    agent.save()

    return Response({"call_id": call.call_id})

@api_view(['POST'])
def check_call_status(request):
    call_id = request.data.get('call_id')

    try:
        # Fetch the call details
        call = CallDetailsModel.objects.get(call_id=call_id)

        # Calculate the call duration so far
        duration_seconds = (timezone.now() - call.start_time).total_seconds()
        duration_minutes = int(duration_seconds // 60) + (1 if duration_seconds % 60 > 0 else 0)

        # Fetch the caller's wallet
        caller_wallet = WalletModel.objects.get(user=call.caller)

        # Define the cost per minute
        cost_per_minute = 150

        # Calculate total cost based on the duration
        total_call_cost = cost_per_minute * duration_minutes

        # Check if the wallet has enough coins left after deducting the total call cost
        remaining_balance = caller_wallet.wallet_coins - total_call_cost

        # If remaining balance is less than 150, disconnect the call
        if remaining_balance < cost_per_minute:
            # Call should be disconnected
            return Response({
                "disconnect": True,
                "message": "Insufficient coins, please end the call."
            }, status=200)

        # Enough coins to continue, return the remaining balance
        return Response({
            "disconnect": False,
            "message": "Call can continue.",
        }, status=200)

    except CallDetailsModel.DoesNotExist:
        return Response({"error": "Call not found"}, status=404)
    except WalletModel.DoesNotExist:
        return Response({"error": "Wallet not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def end_call(request):
    call_id = request.data.get('call_id')
    try:
        call = CallDetailsModel.objects.get(call_id=call_id)
        call.end_time = timezone.now()
        call.save()

        agent_id = call.agent.customer_id
        agent = CustomerModel.objects.get(customer_id=agent_id)
        agent.is_online = True
        agent.save()

        # Calculate exact duration in seconds
        duration_seconds = (call.end_time - call.start_time).total_seconds()

        caller_wallet = WalletModel.objects.get(user=call.caller)
        agent_wallet = WalletModel.objects.get(user=call.agent)

        cost_per_minute = 150 # deduct coin from user
        amount_per_minute = 3 # 3rs to agent commission

        # Calculate cost per second
        cost_per_second = cost_per_minute / 60
        amount_per_second = amount_per_minute / 60

        # Deduct coins from caller
        caller_wallet.wallet_coins -= duration_seconds * cost_per_second
        caller_wallet.save()

        # Add amount to agent's balance
        agent_wallet.call_amount += duration_seconds * amount_per_second
        agent_wallet.total_minutes += duration_seconds / 60
        agent_wallet.total_amount += duration_seconds * amount_per_second
        agent_wallet.save()

        # Create transaction record
        AgentTransactionModel.objects.create(
            agent=agent,
            receiver=call.caller,
            transaction_amount=duration_seconds * amount_per_second,
            transaction_date=datetime.now(),
            # transaction_type='Call'
        )

        return Response({"duration": duration_seconds / 60})
    except CallDetailsModel.DoesNotExist:
        return Response({"error": "Call not found"}, status=404)
    except CustomerModel.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)
    except WalletModel.DoesNotExist:
        return Response({"error": "Wallet not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def buy_call_package(request):
    user_id = request.data.get('user_id')
    package_id = request.data.get('package_id')
    razorpay_payment_id = request.data.get('razorpay_payment_id')

    try:
        user = CustomerModel.objects.get(pk=user_id, status=CustomerModel.NORMAL_USER)
        package = CallPackageModel.objects.get(pk=package_id)
    except (CustomerModel.DoesNotExist, CallPackageModel.DoesNotExist):
        return Response({'error': 'User or package not found'}, status=status.HTTP_404_NOT_FOUND)

    # Create payment entry
    payment = PaymentModel.objects.create(
        user=CustomerModel.objects.get(pk=user_id, status=CustomerModel.NORMAL_USER),
        amount=package.package_price,
        razorpay_id=razorpay_payment_id,
        paid=True,
        created_at=datetime.now()
    )

    # Add messages to user
    wallet = WalletModel.objects.get(user=user_id)
    wallet.wallet_coins += package.total_coins
    wallet.save()

    purchase_date = datetime.now()
    history = UserPurchaseModel.objects.create(
        user=user,
        purchase_amount=package.package_price,
        purchase_date=purchase_date,
        # purchase_type='Call'
    )

    return Response({'message': 'Package purchased successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def list_call_packages(request):
    packages = CallPackageModel.objects.all()
    serializer = CoinsSerializer(packages, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def give_rating(request):
    agent_id = request.data.get('agent')
    user_id = request.data.get('user')
    rating = request.data.get('ratings')

    # Get the agent and user instances
    try:
        agent = CustomerModel.objects.get(customer_id=agent_id)
        user = CustomerModel.objects.get(customer_id=user_id)
    except CustomerModel.DoesNotExist:
        return Response({'error': 'Invalid agent or user ID'}, status=status.HTTP_400_BAD_REQUEST)

    newrating = RatingModel.objects.create(
        agent=agent,
        user=user,
        ratings=rating,
        created_at=datetime.now()
    )

    return Response({'message': "Thank you for your feedback!"}, status=status.HTTP_200_OK)

@api_view(['GET'])
def online_status(request, id):
    user = CustomerModel.objects.get(customer_id = id)
    user.is_online = True
    user.save()
    return JsonResponse({'status': 'success', 'message': 'User is now online.'})

@api_view(['GET'])
def offline_status(request, id):
    user = CustomerModel.objects.get(customer_id=id)
    user.is_online = False
    user.save()
    return JsonResponse({'status': 'success', 'message': 'User is now offline.'})



