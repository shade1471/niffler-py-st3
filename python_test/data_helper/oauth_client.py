import base64

import pkce

from python_test.model.config import Envs
from python_test.model.oauth import OAuthRequest
from python_test.utils.sessions import AuthSession


class OAuthClient:
    """Авторизует по Oauth2.0"""

    session: AuthSession
    base_url: str

    def __init__(self, env: Envs):
        """Генерируем code_verifier и code_challenge. И генерируем basic auth token из секрета сервиса авторизации."""
        self.session = AuthSession(base_url=env.auth_url)
        self.redirect_uri = env.frontend_url + "/authorized"
        # Этот код мы написали самостоятельно и заменили на целевую схему с использованием библиотеки
        # self.code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
        # self.code_verifier = re.sub('[^a-zA-Z0-9]+', '', self.code_verifier)
        #
        # self.code_challenge = hashlib.sha256(self.code_verifier.encode('utf-8')).digest()
        # self.code_challenge = base64.urlsafe_b64encode(self.code_challenge).decode('utf-8')
        # self.code_challenge = self.code_challenge.replace('=', '')
        self.code_verifier, self.code_challenge = pkce.generate_pkce_pair()

        self._basic_token = base64.b64encode(env.auth_secret.encode('utf-8')).decode('utf-8')
        self.authorization_basic = {"Authorization": f"Basic {self._basic_token}"}
        self.token = None

    def get_token(self, username: str, password: str) -> str:
        """Возвращает token oauth для авторизации пользователя с username и password
        1. Получаем jsessionid и xsrf-token куку в сессию.
        2. Получаем code из redirect по xsrf-token'у.
        3. Получаем access_token.
        """
        self.session.get(
            url="/oauth2/authorize",
            params=OAuthRequest(
                redirect_uri=self.redirect_uri,
                code_challenge=self.code_challenge,
            ).model_dump(),
            allow_redirects=True
        )

        self.session.post(
            url="/login",
            data={
                "username": username,
                "password": password,
                "_csrf": self.session.cookies.get("XSRF-TOKEN")
            },
            allow_redirects=True
        )

        token_response = self.session.post(
            url="/oauth2/token",
            data={
                "code": self.session.code,
                "redirect_uri": self.redirect_uri,
                "code_verifier": self.code_verifier,
                "grant_type": "authorization_code",
                "client_id": "client"
            },
        )

        self.token = token_response.json().get("access_token", None)
        return self.token
