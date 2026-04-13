import time
import logging
import requests
from config.settings import TC_SERVER, TC_CLIENT_ID, TC_CLIENT_SECRET, TC_TOKEN_TTL

logger = logging.getLogger("trueconf")


class TrueConfClient:
    def __init__(self):
        self._token = None
        self._token_expires_at = 0

    def _get_token(self):
        if self._token and time.time() < self._token_expires_at:
            return self._token
        resp = requests.post(
            f"{TC_SERVER}/oauth2/v1/token",
            data={
                "grant_type": "client_credentials",
                "client_id": TC_CLIENT_ID,
                "client_secret": TC_CLIENT_SECRET,
            },
            timeout=10,
        )
        resp.raise_for_status()
        self._token = resp.json()["access_token"]
        self._token_expires_at = time.time() + TC_TOKEN_TTL
        return self._token

    def send_message(self, conference_id, text):
        try:
            token = self._get_token()
            resp = requests.post(
                f"{TC_SERVER}/api/v1/conferences/{conference_id}/messages",
                headers={"Authorization": f"Bearer {token}"},
                json={"text": text},
                timeout=10,
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки в TrueConf: {e}")
            return False

    def get_conferences(self):
        try:
            token = self._get_token()
            resp = requests.get(
                f"{TC_SERVER}/api/v1/conferences",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json().get("conferences", [])
        except Exception as e:
            logger.error(f"Ошибка получения конференций: {e}")
            return []
