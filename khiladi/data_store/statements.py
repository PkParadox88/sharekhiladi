from ..data_fetch import statement_fetcher
from ..models import BuyPortfolio, SellPortfolio
from asgiref.sync import sync_to_async
import asyncio


@sync_to_async
def main():
    try:
        buy_data = asyncio.run(statement_fetcher.main(1))
        BuyPortfolio.objects.all().delete()

        transaction_data = buy_data['result']
        for data in transaction_data:
            # print(data)
            buy_detail = BuyPortfolio(
                business_date=data['businessDate'],
                settlement_date=data['settlementDate'],
                symbol=data['stockSymbol'],
                buy_rate=data['rate'],
                quantity=data['quantity'],
                buy_amount=data['amount'],
                broker_commission=data['commAmount'],
                sebon_commission=data['seboComm'],
                dp_charge=data['dpAmount'],
                total_commission=round(float(data['commAmount']) + float(data['seboComm']) + float(data['dpAmount']), 3),
                paid_amount=data['total'],
                effective_rate=round(float(data['total']) / float(data['quantity']), 3),
                payment_status=data['paymentStatus'],
                settlement_status=data['settlementStatus'],
                transaction_number=data['transactionNo'],

            )
            buy_detail.save()
        print("Buy Data updated in Database")

        sell_data = asyncio.run(statement_fetcher.main(2))
        SellPortfolio.objects.all().delete()

        transaction_data = sell_data['result']
        for data in transaction_data:
            try:
                sell_detail = SellPortfolio(
                    business_date=data['businessDate'],
                    settlement_date=data['settlementDate'],
                    symbol=data['stockSymbol'],
                    sell_rate=data['rate'],
                    quantity=data['quantity'],
                    sell_amount=data['amount'],
                    broker_commission=data['commAmount'],
                    sebon_commission=data['seboComm'],
                    dp_charge=data['dpAmount'],
                    total_commission=round(float(data['commAmount']) + float(data['seboComm']) + float(data['dpAmount']), 3),
                    cgt_charge=data['cgt'],
                    received_amount=data['total'],
                    effective_rate=round(float(data['total']) / float(data['quantity']), 3),
                    payment_status=data['paymentStatus'],
                    settlement_status=data['settlementStatus'],
                    transaction_number=data['transactionNo'],
                )
                sell_detail.save()
            except Exception as e:
                print(e)
        print("Sell Data updated in Database")

    except Exception as e:
        print(e)

