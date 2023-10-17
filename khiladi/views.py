from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
from .data_fetch import session
from .data_fetch import data_fetcher, turnover_fetcher
from .data_fetch import statement_fetcher
from .data_fetch import socket_data
from .data_store import statements
from .models import *
import asyncio
from .tasks import fetch_sessions, fetch_data


async def homepage(request):
    # Trigger the background tasks without using 'await'
    fetch_sessions()
    fetch_data()

    # Render the page immediately
    return render(request, 'khiladi/homepage.html', context={'stocks': []})


async def update_data(request):
    data = await data_fetcher.main()
    return JsonResponse({'stocks': data})


def dashboard(request):
    return render(request, 'khiladi/dashboard.html', {})


def api_indices(request):
    data = list(LiveIndex.objects.values())
    return JsonResponse({'indices': data}, safe=False)


async def fetch_turnover(request):
    data = await turnover_fetcher.main()
    return JsonResponse({'turnover': data})


def buy_portfolio(request):
    data = BuyPortfolio.objects.all()
    table_data = {'buy_portfolio': data}
    return render(request, 'khiladi/buy_portfolio.html', table_data)


def buy_portfolio_refresh(request):
    asyncio.run(statements.main())
    data = BuyPortfolio.objects.all()
    table_data = {'buy_portfolio': data}
    return render(request, 'khiladi/buy_portfolio.html', table_data)


def sell_portfolio(request):
    data = SellPortfolio.objects.all()
    table_data = {'sell_portfolio': data}
    return render(request, 'khiladi/sell_portfolio.html', table_data)


def sell_portfolio_refresh(request):
    asyncio.run(statements.main())
    data = SellPortfolio.objects.all()
    table_data = {'sell_portfolio': data}
    return render(request, 'khiladi/sell_portfolio.html', table_data)


def summary_portfolio(request):

    obj = SummaryPortfolio.objects.all()
    print(obj)
    context = {'summary_portfolio': obj, }
    return render(request, 'khiladi/buy_portfolio.html', context)


async def livedata(request):

    return render(request, 'khiladi/livedata.html', {})


async def news(request):

    return render(request, 'khiladi/news.html', {})

