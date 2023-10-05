from django.shortcuts import render
from django.http import JsonResponse
from .data_fetch import data_fetcher
from .data_fetch import session
import asyncio


async def homepage(request):
    # Fetch data asynchronously
    try:
        print("Session login...")
        asyncio.run(session.SessionManager().get_sessions())
        print("Fetching data...")
        data = await data_fetcher.main()

    except Exception as e:
        data = []  # If there is an error, return an empty list

    context = {'stocks': data}
    return render(request, 'khiladi/homepage.html', context)


async def update_data(request):
    data = await data_fetcher.main()
    return JsonResponse({'stocks': data})


async def dashboard(request):

    return render(request, 'khiladi/dashboard.html', {})

