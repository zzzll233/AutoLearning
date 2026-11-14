import requests
import pytest

def test_login_then_get_current_user():
    base_url = "https://dummyjson.com"
    '''
    测试登录后获取当前用户信息
    1. 用 requests.post 发送 POST 请求到 https://dummyjson.com/auth/login，
       传入 account = {"username": "emilys", "password": "emilyspass"}。
    2. 断言响应状态码为 200。
    3. 从响应中提取 accessToken。
    4. 用 requests.get 发送 GET 请求到 https://dummyjson.com/auth/me，
       传入 Authorization: Bearer <token>。
    5. 断言响应状态码为 200，响应里的 username 等于 account["username"]。
    '''
    account = {"username": "emilys", "password": "emilyspass"}

    api_session = requests.Session()
    login = api_session.post(
        f"{base_url}/auth/login",
        json=account,
        timeout=10,
    )
    assert login.status_code == 200

    token = login.json()["accessToken"]
    assert token is not None

    # 测试用例：登录后获取当前用户信息
    api_session = requests.Session()
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

# 为参数化测试函数添加文档字符串和注释，说明测试场景和预期行为
@pytest.mark.parametrize("token", [None, "invalid-demo-token"])
def test_get_current_user_rejects_bad_credentials(token):
    base_url = "https://dummyjson.com"
    api_session = requests.Session()
    headers = {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    
    # 测试用例：
    # 1. 测试 token 为空时的情况。
    # 2. 测试 token 为无效值时的情况。
    api_session = requests.Session()
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