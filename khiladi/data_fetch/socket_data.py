import nest_asyncio
import websockets
import json

creds_file = "khiladi/data_fetch/_secrets.json"
token_file = "khiladi/data_fetch/_tokens.json"

nest_asyncio.apply()


async def load_creds():
    with open(creds_file, 'r') as file:
        creds_json = json.load(file)
    if "ids" in creds_json and creds_json["ids"]:
        creds_dict = creds_json["ids"]
        return creds_dict


async def load_token():
    with open(token_file, 'r') as file:
        token_json = json.load(file)
    if "tokens" in token_json and token_json["tokens"]:
        tokens_dict = token_json["tokens"]
        return tokens_dict


async def main(data_queue):
    credentials = await load_creds()

    tms_id = credentials["ID1"]["tmsId"]
    member_id = credentials["ID1"]["memberId"]
    client_id = credentials["ID1"]["clientId"]
    user_id = credentials["ID1"]["userId"]

    websocket_url = f"wss://{tms_id}.nepsetms.com.np//tmsapi/socket?memberId={member_id}&clientId={client_id}&dealerId=&userId={user_id}"

    tokens = await load_token()
    headers = {"Cookie": tokens["ID1_01"]["Cookie"],
               "X-Xsrf-Token": tokens["ID1_01"]["X-XSRF-TOKEN"],
               "Origin": "https://tms19.nepsetms.com.np",
               "Sec-Websocket-Extensions": "permessage-deflate; client_max_window_bits",
               "User-Agent": tokens["ID1_01"]["User-Agent"],
               "Accept-Encoding": "gzip, deflate, br"
               }

    try:
        async with websockets.connect(websocket_url, extra_headers=headers) as websocket:
            print("WebSocket connection established successfully")

            # First message
            message_to_send_1 = {
                "header": {"channel": "@control", "transaction": "start_index"},
                "payload": {"argument": "undefined"}
            }

            # Serialize the first message to a JSON string
            json_message_1 = json.dumps(message_to_send_1)

            # Send the first message
            await websocket.send(json_message_1)
            print(f"Sent message 1: {json_message_1}")

            # Second message
            message_to_send_2 = {
                "header": {"channel": "@control", "transaction": "start_top25securities"},
                "payload": {"argument": "undefined"}
            }

            # Serialize the second message to a JSON string
            json_message_2 = json.dumps(message_to_send_2)

            # Send the second message
            await websocket.send(json_message_2)
            print(f"Sent message 2: {json_message_2}")

            while True:
                # Receive data from the WebSocket server
                data = json.loads(await websocket.recv())
                json_data = data
                # print(f"Received data: {json_data}")
                await data_queue.put(json_data)

    except websockets.exceptions.ConnectionClosed:
        print("WebSocket connection closed.")


