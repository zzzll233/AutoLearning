import requests
import pytest

def test_login_then_get_current_user():
    base_url = "https://dummyjson.com"
    account = {"username": "emilys", "password": "emilyspass"}

    login = requests.post(
        f"{base_url}/auth/login",
        json=account,
        timeout=10,
    )
    assert login.status_code == 200

    token = login.json()["accessToken"]
    assert token is not None

    response = api_session.get(
        f"{base_url}/auth/me",
        headers = {"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    assert response.status_code == 200
    user = response.json()
    assert user["username"] == account["username"]
    # 在这里用 requests.get 请求 /auth/me。
    # 用 headers 传入 Authorization: Bearer <token>。
    # 断言状态码为 200，响应里的 username 等于 account["username"]。

@pytest.mark.parametrize("token", [None, "invalid-demo-token"])
def test_get_current_user_rejects_bad_credentials(token):
    headers = {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    
    response = api_session.get(
    f"{base_url}/auth/me",
    headers = headers,
    timeout=10,
    )
    assert response.status_code == 401
    assert "username" not in response.json()
    # 用 requests.get 请求 https://dummyjson.com/auth/me。
    # 传入 headers=headers 和 timeout=10。
    # 断言状态码为 401，并检查响应里没有 username 字段。