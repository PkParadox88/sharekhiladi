from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('update_data/', views.update_data, name='update_data'),
    path('portfolio/buy', views.buy_portfolio, name='buy_portfolio'),
    path('portfolio/buy/refresh', views.buy_portfolio_refresh, name='buy_portfolio_refresh'),
    path('portfolio/sell', views.sell_portfolio, name='sell_portfolio'),
    path('portfolio/sell/refresh', views.sell_portfolio_refresh, name='sell_portfolio_refresh'),
    path('portfolio/summary', views.summary_portfolio, name='summary_portfolio'),
    path('livedata/', views.livedata, name='livedata'),
    path('news/', views.news, name='news'),
    # path('stop/', views.stop_all_async, name='stop_all_async'),
    path('khiladi/api/indices/', views.api_indices, name='api_indices'),
    path('khiladi/fetch/turnover/', views.fetch_turnover, name='fetch_turnover'),
]
