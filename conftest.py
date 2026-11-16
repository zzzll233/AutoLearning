import json
from pathlib import Path

import pytest
import requests
import mysql.connector

from qa_settings import QA_BASE_URL

@pytest.fixture
def qa_training_url():
    return QA_BASE_URL

@pytest.fixture
def api_session():
    with requests.Session() as session:
        yield session

@pytest.fixture(scope="module")
def db_conn():
    '''
    连接数据库并返回连接对象
    '''
    config_path = Path(__file__).with_name("db_config.local.json")
    with config_path.open(encoding="utf-8") as file:
        config = json.load(file)
    with mysql.connector.connect(**config) as connection:
        connection.ping(reconnect=True, attempts=3, delay=1)
        yield connection