from typing import Any

import requests

class APIClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.token: str | None = None

    def initialise_account(self) -> requests.Response:
        response = self.session.get(f"{self.base_url}/init", timeout=10)
        response.raise_for_status()

        response_data = response.json()
        self.token = response_data["access_token"]
        self.session.headers.update(
            {"Authorization": f"Bearer {self.token}"}
        )

        return response

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        authenticated: bool = True,
    ) -> requests.Response:
        headers = None if authenticated else {"Authorization": ""}

        return self.session.request(
            method=method,
            url=f"{self.base_url}{path}",
            params=params,
            json=json,
            headers=headers,
            timeout=10,
        )
        