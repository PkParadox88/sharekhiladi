import json
import aiohttp

creds_file = "khiladi/data_fetch/_secrets.json"
token_file = "khiladi/data_fetch/_tokens.json"


data_id = "ID1"


class Statement:
    def __init__(self, data_id):
        self.clients_dict = None
        self.data_id = data_id
        self.tms_id = ""
        self.client_id = 0
        self.auth_tokens = {}
        self.headers = {}
        self.url = None
        self.token_file = token_file
        self.creds_file = creds_file

    async def load_tokens(self):
        try:
            with open(self.token_file, 'r') as file:
                token_json = json.load(file)
            if "tokens" in token_json and token_json["tokens"]:
                self.auth_tokens = token_json["tokens"]
        except Exception as e:
            print(f"Error loading tokens: {e}")

    async def get_client_id(self):
        with open(self.creds_file, "r") as f:
            json_data = json.load(f)
        self.clients_dict = json_data.get("ids", {})
        cred = self.clients_dict.get(self.data_id)

        if cred:
            self.tms_id = cred.get('tmsId')
            self.client_id = cred.get('clientId')

    async def get_header(self):
        for unique_login_id, headers in self.auth_tokens.items():
            if self.data_id == unique_login_id[:3]:
                self.tms_id = headers["Referer"][8:13]
                self.headers = headers

    async def get_transactions_list(self, data):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(self.url, json=data) as r:
                r.raise_for_status()
                j = await r.json()
                # print(j)
                return j

    async def get_statement(self, data_url):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(data_url) as r:
                r.raise_for_status()
                j = await r.json()
                return j

    async def process_data_list(self, buy_or_sell):
        try:
            await self.load_tokens()
            await self.get_client_id()
            await self.get_header()
            print("Getting statements data...")
            # print(self.auth_tokens)
            # print(self.client_id)
            # print(self.headers)

            self.url = f"https://{self.tms_id}.nepsetms.com.np/tmsapi/fundApi/settlementPayment/"

            payment_status = ["NET_SETTLEMENT_SUCCESS", "PAID", "MANUALLY_PAID", "NET_SETTLEMENT_PROCESSING",
                              "NCHL_PAYMENT_PENDING", "NET_SETTLEMENT_PENDING", "NCHL_PROCESSING", "PAYMENT_PENDING",
                              "NCHL_APPROVED", "NET_SETTLEMENT_APPROVED", "PAYMENT_DUE"]
            data = {"orderBy": "", "orderDirection": "DESC", "pageNumber": 1, "pageSize": 100, "buyOrSell": buy_or_sell,
                    "businessDateFrom": None, "businessDateTo": None, "clientId": self.client_id,
                    "paymentStatusList": payment_status, "memberBranchId": None}
            print(self.url)
            _data = await self.get_transactions_list(data)
            # print(_data)

            result_list = []
            _data = _data['result']
            for item in _data:
                # _id = item['id']
                business_date = item['businessDate']
                settlement_date = item['settlementDate']
                # buyOrSell = item['buyOrSell']
                # totalAmount = item['totalAmount']
                # amountPending = item['amountPending']
                payment_status = item['paymentStatus']

                data_url = f"https://{self.tms_id}.nepsetms.com.np/tmsapi/fundApi/settlementPayment/" \
                           f"getSettlementTransactionDetails?clientDealerId={self.client_id}&date={settlement_date}" \
                           f"&tradeDate={business_date}&buyOrSell={buy_or_sell}&paymentStatus={payment_status}"

                result = await self.get_statement(data_url)
                for transaction in result:
                    transaction['businessDate'] = business_date
                    transaction['settlementDate'] = settlement_date
                    transaction['paymentStatus'] = payment_status
                # print(result)

                result_list.extend(result)
            print(f"Data extracted successfully")

            json_data = {
                # "transaction_list": _data,
                "result": result_list
            }

            # print(json_data)
            return json_data

        except Exception as e:
            print(e)
            return e


async def main(buy_or_sell):
    buy_or_sell = buy_or_sell
    stat = Statement(data_id)
    json_data = await stat.process_data_list(buy_or_sell)
    return json_data

