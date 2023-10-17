from django.db import models
from datetime import datetime


class BuyPortfolio(models.Model):
    id = None
    business_date = models.DateField(default=datetime.today)
    settlement_date = models.DateField(default=datetime.today)
    symbol = models.CharField(max_length=10, default="API")
    buy_rate = models.FloatField(default=0.0)
    quantity = models.IntegerField(default=0)
    buy_amount = models.FloatField(default=0.0)
    broker_commission = models.FloatField(default=0.0)
    sebon_commission = models.FloatField(default=0.0)
    dp_charge = models.FloatField(default=0.0)
    total_commission = models.FloatField(default=0.0)
    paid_amount = models.FloatField(default=0.0)
    effective_rate = models.FloatField(default=0.0)
    payment_status = models.CharField(max_length=30, default="NET_SETTLEMENT_SUCCESS")
    settlement_status = models.CharField(max_length=30, default="SETTLED")
    transaction_number = models.BigIntegerField(default=0, primary_key=True)


class SellPortfolio(models.Model):
    id = None
    business_date = models.DateField(default=datetime.today)
    settlement_date = models.DateField(default=datetime.today)
    symbol = models.CharField(max_length=10, default="API")
    sell_rate = models.FloatField(default=0.0)
    quantity = models.IntegerField(default=0)
    sell_amount = models.FloatField(default=0.0)
    broker_commission = models.FloatField(default=0.0)
    sebon_commission = models.FloatField(default=0.0)
    dp_charge = models.FloatField(default=0.0)
    total_commission = models.FloatField(default=0.0)
    cgt_charge = models.FloatField(default=0.0)
    received_amount = models.FloatField(default=0.0)
    effective_rate = models.FloatField(default=0.0)
    payment_status = models.CharField(max_length=30, default="NET_SETTLEMENT_SUCCESS")
    settlement_status = models.CharField(max_length=30, default="SETTLED")
    transaction_number = models.BigIntegerField(default=0, primary_key=True)


class SummaryPortfolio(models.Model):
    id = None
    date = models.DateField(default=datetime.today)
    type = models.CharField(max_length=10, default="BUY")
    symbol = models.CharField(max_length=10, default="API")
    rate = models.FloatField(default=0.0)
    quantity = models.IntegerField(default=0)
    amount = models.FloatField(default=0.0)
    pl_status = models.CharField(max_length=10, default="Profit")
    pl_percent = models.FloatField(default=0.0)
    pl_amount = models.FloatField(default=0.0)
    holding_days = models.IntegerField(default=0)
    transaction_number = models.BigIntegerField(default=0, primary_key=True)


class LiveTable(models.Model):
    symbol = models.CharField(max_length=10, default="API")
    ltp = models.FloatField(default=0.0)
    percentChange = models.FloatField(default=0.0)
    change = models.FloatField(default=0.0)
    open = models.FloatField(default=0)
    high = models.FloatField(default=0)
    low = models.FloatField(default=0)
    volume = models.BigIntegerField(default=0)
    lastTradedVolume = models.IntegerField(default=0)
    lastTradedTime = models.CharField(max_length=30, default="")
    previousClose = models.FloatField(default=0.0)


class LiveIndex(models.Model):
    id = None
    indexCode = models.CharField(max_length=20, default="NEPSE", primary_key=True)
    indexValue = models.FloatField(default=0.0)
    prevCloseIndex = models.FloatField(default=0.0)
    change = models.FloatField(default=0.0)
    percentageChange = models.FloatField(default=0.0)
