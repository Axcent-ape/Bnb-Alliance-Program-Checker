from core.utils import Web3Utils
from fake_useragent import UserAgent
import aiohttp


class CheckEligible:
    def __init__(self, key: str, proxy: str = None):
        self.web3_utils = Web3Utils(key=key)
        self.proxy = f"http://{proxy}" if proxy is not None else None

        headers = {
            'User-Agent': UserAgent(os='windows').random
        }

        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, cookie_jar=aiohttp.CookieJar())

    async def get_challenge(self):
        json_data = {"address": self.web3_utils.acct.address}
        resp = await self.session.post("https://dappbay.bnbchain.org/api/v1/user/challenge", json=json_data, proxy=self.proxy)

        return (await resp.json()).get('challenge')

    async def login(self):
        json_data = {
            "address": self.web3_utils.acct.address,
            "signedMsg": self.web3_utils.get_signed_code(await self.get_challenge())
        }

        resp = await self.session.post("https://dappbay.bnbchain.org/api/v1/user/login", json=json_data, proxy=self.proxy)
        self.session.cookie_jar.update_cookies(resp.cookies)

        return (await resp.text()) == "true"

    async def check_eligible(self):
        resp = await self.session.get("https://dappbay.bnbchain.org/api/v1/airdrop2-campaign/user-info", proxy=self.proxy)
        resp_json = await resp.json()

        return resp_json.get("isLevel1"), resp_json.get("isLevel2")

    async def logout(self):
        await self.session.close()
