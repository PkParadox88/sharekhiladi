import asyncio
import nest_asyncio
from aiohttp import ClientSession, ClientError
from base64 import b64encode
from easyocr import Reader
import json
import logging
from os import path
from yarl import URL

nest_asyncio.apply()

logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

nos_of_logins_per_id = 1
retry_limit = 5

token_file = "khiladi/data_fetch/_tokens.json"
creds_file = "khiladi/data_fetch/_secrets.json"


class AuthManager:
    def __init__(self, tms_id, ocr):
        self.tms_id = tms_id
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0'
        self.ocr = ocr

    async def get_captcha_id(self, session):
        id_url = f"https://{self.tms_id}.nepsetms.com.np/tmsapi/captcha/id"
        id_resp = await session.get(id_url)
        captcha_id = (await id_resp.json())['id']
        return captcha_id

    async def get_captcha_image(self, session, captcha_id):
        img_url = f"https://{self.tms_id}.nepsetms.com.np/tmsapi/captcha/image/{captcha_id}"
        img_resp = await session.get(img_url)
        captcha_data = await img_resp.read()
        return captcha_data

    async def login(self, username, password):
        try:
            async with ClientSession(headers={'User-Agent': self.user_agent}) as session:
                captcha_id = await self.get_captcha_id(session)
                captcha_data = await self.get_captcha_image(session, captcha_id)
                result = self.ocr.readtext(captcha_data)
                captcha = result[0][1]

                enc_pwd = b64encode(password.encode()).decode()
                login_data = {
                    "userName": username,
                    "password": enc_pwd,
                    "captchaIdentifier": captcha_id,
                    "userCaptcha": captcha
                }

                auth_url = URL.build(scheme="https", host=f"{self.tms_id}.nepsetms.com.np", path="/tmsapi/authenticate")

                async with session.post(auth_url, json=login_data) as auth_resp:
                    status = auth_resp.status

                    if status == 200:
                        response_json = await auth_resp.json()
                        user_id = response_json['data']['user']['id']

                        cookies = session.cookie_jar.filter_cookies(auth_url)
                        cookie_dict = {name: cookie.value for name, cookie in cookies.items()}
                        xsrf_token = cookie_dict['XSRF-TOKEN']
                        # cookies = auth_resp.cookies
                        cookie_str = "; ".join([f"{name}={value}" for name, value in cookie_dict.items()])

                        session_id = b64encode(f"MTI=-{xsrf_token}".encode()).decode()

                        headers = {
                            "Content-Type": "application/json",
                            "Cookie": cookie_str,
                            "Host-Session-Id": session_id,
                            "Request-Owner": str(user_id),
                            "Referer": f"https://{self.tms_id}.nepsetms.com.np",
                            "User-Agent": self.user_agent,
                            "X-XSRF-TOKEN": xsrf_token
                        }

                        print(f"Logged in successfully: {captcha}")
                        return headers

                    elif status == 401:
                        logger.warning(f"CAPTCHA_VALIDATION_FAILED: {captcha}")

                    elif status == 400:
                        logger.error(f"Error! [E_C400]: INVALID_REQUEST {login_data}")

                    else:
                        response_json = await auth_resp.json()
                        logger.error(f"Error! [E_CR_100]: Unknown response {response_json}")

        except ClientError as e:
            logger.error(f"Error! [E_CR_101]: AIOHTTP ClientError occurred: {e}")

        except Exception as e:
            logger.error(f"Error! [E_CR_102]: An exception occurred during login: {e}")


class SessionManager:

    def __init__(self):
        self.creds = {}
        self.tokens = {}
        self.ocr = None

    async def login(self, tms_id, username, password):
        auth_manager = AuthManager(tms_id, self.ocr)
        headers = await auth_manager.login(username, password)
        return headers

    async def retry_login(self, tms_id, username, password):
        if not self.ocr:
            self.ocr = Reader(['en'])

        retry_interval = 1
        retry_backoff_factor = 1.5

        retry_count = 0
        while retry_count < retry_limit:
            headers = await self.login(tms_id, username, password)
            if headers:
                return headers

            logger.warning(f"Retry attempt {retry_count + 1} failed. Retrying in {retry_interval} second(s)...")
            await asyncio.sleep(retry_interval)
            retry_count += 1
            retry_interval *= retry_backoff_factor

        logger.critical(f"Failed after {retry_count} retry attempts.")

    async def concurrent_login(self, unique_login_id, tms_id, username, password):
        headers = await self.retry_login(tms_id, username, password)

        # Store the headers value in the session manager object
        setattr(self, unique_login_id, headers)

        self.tokens[unique_login_id] = headers
        print(f"Logged in {tms_id} with {unique_login_id}. Headers: {headers}")

    async def login_all(self):
        await self.get_all_credentials()

        tasks = []
        for login_id, cred in self.creds.items():
            tms_id = cred.get('tmsId')
            username = cred.get('username')
            password = cred.get('password')

            if login_id and tms_id and username and password:
                for i in range(1, nos_of_logins_per_id + 1):
                    unique_login_id = f"{login_id}_{i:02}"

                    task = asyncio.create_task(self.concurrent_login(unique_login_id, tms_id, username, password))
                    tasks.append(task)
        await asyncio.gather(*tasks)

        await self.save_auth()

    async def save_auth(self):
        output = {"tokens": self.tokens}
        # print(f"\nSaving tokens...{output}\n")
        with open(token_file, "w") as file:
            json.dump(output, file, indent=4)

    async def load_auth(self):
        with open(token_file, 'r') as file:
            token_json = json.load(file)
        if "tokens" in token_json and token_json["tokens"]:
            self.tokens = token_json["tokens"]

    async def get_credentials(self, unique_login_id):
        # for login_id, item in self.creds.items():
        #     if unique_login_id.startswith(item.get("login_id")):
        cred = self.creds.get(unique_login_id)
        if cred:
            tms_id = cred.get('tmsId')
            username = cred.get('username')
            password = cred.get('password')

            return tms_id, username, password

    async def get_all_credentials(self):
        try:
            with open(creds_file, "r") as f:
                json_data = json.load(f)
            self.creds = json_data["ids"]

        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"An error occurred while retrieving credentials: {e}")

    @staticmethod
    async def validate_session(tms_id, headers):
        # "https://tms19.nepsetms.com.np/tmsapi/dnaApi/exchange/sessionCheck"
        check_url = f"https://{tms_id}.nepsetms.com.np/tmsapi/stock/last-updated-time"

        async with ClientSession() as session:
            try:
                async with session.get(check_url, headers=headers) as response:
                    if response.status == 200:
                        rj = await response.json()
                        print(rj)
                        return True

            except ClientError as e:
                logger.error(f"An error occurred while validating session: {e}")
        return False

    async def process_token(self, unique_login_id, headers):
        login_id = unique_login_id[:3]
        tms_id, username, password = await self.get_credentials(login_id)

        if not headers:
            new_headers = await self.retry_login(tms_id, username, password)
            if new_headers:
                return unique_login_id, new_headers
            return unique_login_id, None
        else:
            is_valid_session = await self.validate_session(tms_id, headers)
            if is_valid_session:
                return unique_login_id, headers
            else:
                new_headers = await self.retry_login(tms_id, username, password)
                if new_headers:
                    return unique_login_id, new_headers
                return unique_login_id, None

    async def validate_all_sessions(self):
        if not self.creds:
            await self.get_all_credentials()

        unique_ids = {f"{key}_{i:02}" for i in range(1, nos_of_logins_per_id + 1) for key in self.creds.keys()}
        missing_ids = unique_ids - set(self.tokens.keys())
        self.tokens.update({missing_id: {} for missing_id in missing_ids})

        tasks = [
            asyncio.create_task(self.process_token(unique_login_id, headers))
            for unique_login_id, headers in self.tokens.items()
        ]

        results = await asyncio.gather(*tasks)
        new_tokens = {k: v for k, v in results if v is not None}

        old_len = len(self.tokens)
        new_len = len(new_tokens)
        self.tokens = new_tokens

        await self.save_auth()

        if new_len == old_len:
            print(f"{new_len} AuthToken are refreshed or validated.")
            return True

        print(f"{new_len} AuthToken refreshed,\n{old_len - new_len} AuthToken cannot be refreshed.")
        return False

    async def get_sessions(self):
        validate_session = True

        if path.exists(token_file):
            await self.load_auth()

        if not self.tokens:
            await self.login_all()
            # validate_session = False

        if validate_session and self.tokens:
            await self.validate_all_sessions()
            await asyncio.sleep(0.1)
            if self.tokens:
                # print(f"Valid Sessions: {self.tokens}")
                return self.tokens
            return False


if __name__ == "__main__":
    asyncio.run(SessionManager().get_sessions())

