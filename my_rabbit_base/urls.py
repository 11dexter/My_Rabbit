"""
URL configuration for my_rabbit_base project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from my_rabit_app import views


urlpatterns = [
    path('admin/', admin.site.urls),  # admin page
    path('', views.home, name='home'),  # home page
    path('login/', views.login, name='login'),  # login page
    # path('reg', views.reg, name='reg'),  # registration page
    path('users/', views.registered_users, name='users'),  # All users view page (both users and agents)
    path('add_user/', views.add_user, name='add_user'),  # Page for add a new user
    path('delete_user/', views.delete_user, name='delete_user'),  # Page for deleting a user
    path('wallet_normal_user', views.wallet_normaluser, name='wallet_normal_users'),  # wallet page for normal user
    path('wallet_agent_user', views.wallet_agentuser, name='wallet_agent_users'),  # wallet page for agent user
    path('normal_user', views.normal_user, name='normal_user'),  # Page for viewing all users
    path('agent_user', views.agent_user, name='agent_user'),  # Page for viewing all agents
    path('logout', views.logout, name='logout'),  # Page for logging out
    path('coin_package', views.coin_package, name='coin_package'),  # Page for viewing all coin packages
    path('delete/coin_package/<int:coin_id>/', views.delete_coin_package, name='delete_coin_package'),  # Delete coin package
    path('add_package', views.add_package, name='add_package'),  # Add package to coin package
    path('history_normal_user', views.user_history, name='history_normal_users'),  # Page for viewing purchases of user
    path('history_agent_user', views.agent_history, name='history_agent_users'),  # Page for viewing withdrawals of agents
    path('search/', views.search_results, name='search_results'), # view for all user search option
    path('agent/search/', views.agent_search, name='agent_search'),  # view for searching a agent
    path('user/search/', views.user_search, name='user_search'),  # view for searching a user
    path('all_agents', views.agent_report, name='agent_report'),   # view for all agents withdrawals
    path('report/', views.report_view, name='report'),  # view for all report (both agents and users)
    path('get_payment_data/', views.get_payment_data, name='get_payment_data'),  # retrieving data for index page chart


    #  API URLs
    path('login_user/', views.customers, name='user_data'),
    path('all_users/', views.all_users, name='all_users'),
    path('all_agents/', views.all_agents, name='all_agents'),
    path('check_user/<str:mobileno>', views.check_users, name='check_user'),  # Not getting postman result
    path('update_profile/<int:id>', views.update_profile, name='update_profile'),
    path('wallet/<int:id>', views.wallet, name='wallet'),
    path('withdrawal/<int:id>', views.withdrawal, name='withdrawal'),
    path('start-call/', views.start_call, name='start-call'), # need edit
    path('check-call-status/', views.check_call_status, name='check_call_status'),  # need edit
    path('end-call/', views.end_call, name='end-call'),  # need to edit .this isnt done
    path('call_purchase/', views.buy_call_package, name='call_package'),
    path('call_package/', views.list_call_packages, name='call_packages'),
    path('give_rating/', views.give_rating, name='rating'),
    path('online_status/<int:id>', views.online_status, name='online-status'),
    path('offline_status/<int:id>', views.offline_status, name='offline-status'),
]