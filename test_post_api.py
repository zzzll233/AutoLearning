import requests
import pytest

@pytest.fixture
def base_url():
    return "https://jsonplaceholder.typicode.com"

# 测试获取帖子详情
@pytest.mark.parametrize("post_id", [1,2])
def test_get_post_by_id(post_id, base_url, api_session):
    response = api_session.get(
    f"{base_url}/posts/{post_id}",
    timeout=10,
)

    assert response.status_code == 200 # 检查响应状态码为 200

    post = response.json()
    assert post["id"] == post_id

# 测试获取用户帖子
@pytest.mark.parametrize("user_id, expected_has_posts", [(1, True),(999, False)])
def test_get_posts_by_user_id(user_id, expected_has_posts, base_url, api_session):
    response = api_session.get(
        f"{base_url}/posts",
        params = {"userId": user_id},
        timeout=10,
        )

    assert response.status_code == 200 # 检查响应状态码为 200

    posts = response.json()
    assert isinstance(posts, list) # 检查是否为列表
    assert expected_has_posts == bool(posts) # 检查是否有帖子

    for post in posts:
        assert post["userId"] == user_id # 检查帖子用户ID与预期用户ID一致

# 测试创建帖子
def test_create_post(base_url, api_session):
    payload ={
        "title": "QA practice",
        "body": "My first automated POST test",
        "userId": 1
    }

    response = api_session.post(
        f"{base_url}/posts",
        json = payload,
        timeout=10
    )
    assert response.status_code == 201 # 检查响应状态码为 201

    posts = response.json()
    assert isinstance(posts, dict) # 检查是否为字典
    assert posts["title"] == payload["title"] # 检查标题是否与预期一致
    assert posts["body"] == payload["body"] # 检查内容是否与预期一致
    assert posts["userId"] == payload["userId"] # 检查用户ID是否与预期一致
    assert posts["id"] > 0 # 检查是否有ID

def test_session_sends_cookie(api_session):
    api_session.get(
        "https://httpbingo.org/cookies/set",
        params={"qa_demo": "abc123"},
        allow_redirects=False,
        timeout=10,
    )
    assert api_session.cookies.get("qa_demo") == "abc123"

    response = api_session.get("https://httpbingo.org/cookies", timeout=10)
    assert response.status_code == 200 # 检查响应状态码为 200

    received_cookies = response.json()["cookies"]
    # 补一条断言，检查服务器收到的 qa_demo 值是 abc123。
    assert received_cookies["qa_demo"] == "abc123"

    with requests.Session() as new_session:
        # 新会话不应该发送 qa_demo Cookie
        response = new_session.get("https://httpbingo.org/cookies", timeout=10)
        assert response.status_code == 200 # 检查响应状态码为 200

        received_cookies = response.json()["cookies"]
        print("新会话发送的 Cookie", received_cookies)
        assert "qa_demo" not in received_cookies


@pytest.mark.parametrize(
    "token, expected_status",
    [
        (None, 401),
        ("qa-demo-token", 200),
    ],
)
def test_bearer_header(api_session, token, expected_status):
    headers = {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"

    response = api_session.get(
        "https://httpbingo.org/bearer",
        headers = headers,
        timeout = 10
        )

    assert response.status_code == expected_status


