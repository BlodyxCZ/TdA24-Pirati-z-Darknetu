import pytest
import requests

session = requests.Session()

@pytest.fixture
def requestSession():
    return session

@pytest.fixture
def url():
    return "http://localhost"

# Good enough
def get_random_lecturer():
    return {
        "title_before": "Bc.",
        "first_name": "Jan",
        "middle_name": "",
        "last_name": "Novák",
        "title_after": "",
        "picture_url": "https://example.com/",
        "location": "Earth",
        "claim": "None",
        "bio": "asdf",
        "price_per_hour": 200,
    }

def get_special_lecturer():
    # TODO: find out what this should do
    return get_random_lecturer()