import time
import aiohttp

TOKEN_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"

class OpenSkyTokenManager:
    def __init__(self, client_id: str, client_secret: str):
        self._client_id = client_id
        self._client_secret = client_secret
        self._token: str | None = None
        self._expires_at: float = 0.0

    async def get_token(self, session: aiohttp.ClientSession) -> str:
        if self._token and time.monotonic() < self._expires_at:
            return self._token
        async with session.post(
            TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()
        self._token = data["access_token"]
        self._expires_at = time.monotonic() + data.get("expires_in", 1800) - 30
        return self._token