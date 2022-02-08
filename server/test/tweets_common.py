from typing import Tuple

from fastapi.testclient import TestClient

from app.tweets_common.helper_functions import ModelType
from app.tweets_common.models import Overview


def overview_helper(
    base_path: str, inserted_tweets: Tuple[ModelType, ModelType], client: TestClient
):
    def get_strftime(tweet: ModelType):
        return tweet.created_at.strftime(r"%Y-%m-%d")

    response = client.get(base_path + "overview")
    assert response.status_code == 200

    response_json = response.json()
    required_keys = Overview.__fields__.keys()
    for tweet in response_json:
        assert tweet.keys() == required_keys

    created_dates = {tweet["created_date"] for tweet in response_json}
    tweet1, tweet2 = inserted_tweets
    assert created_dates == {
        get_strftime(tweet1),
        get_strftime(tweet2),
    }


def list_tweets_helper(
    base_path: str, inserted_tweets: Tuple[ModelType, ModelType], client: TestClient
):
    response = client.get(base_path)
    assert response.status_code == 200
    json_response = response.json()

    assert isinstance(json_response, list)
    assert len(json_response) == 2

    tweet1, tweet2 = inserted_tweets

    assert json_response[0]["text"] == tweet1.text
    assert json_response[1]["text"] == tweet2.text

    assert json_response[0]["username"] == tweet1.username
    assert json_response[1]["username"] == tweet2.username
