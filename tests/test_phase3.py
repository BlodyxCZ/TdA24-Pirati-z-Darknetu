import pytest
import requests
import uuid
from urllib.parse import urljoin

# noinspection PyUnresolvedReferences
from .fixtures import *

# noinspection PyStatementEffect
{
    'displayName': 'Fáze 3: Backend',
    'description': 'To, co nikdo nevidí.',
    'startsAt': '2023-11-27T07:00:00.00Z'
}

def check_uuid(response_json, compare_uuid: str = None):
    assert "uuid" in response_json, \
        f"The response should contain the key uuid, but it doesn't."
    assert isinstance(response_json["uuid"], str), \
        f"The uuid should be a string, but it is {type(response_json['uuid'])}."
    if compare_uuid:
        assert response_json["uuid"] == compare_uuid, \
            f"The response should contain the uuid {compare_uuid}, but it doesn't."

def parse_response(response: requests.Response, exp_type: type = dict):
    response_json = response.json()
    assert isinstance(response_json, exp_type), \
        f"The response should contain an object, but it contains {type(response_json)}."
        
    return response_json

def common_check(response: requests.Response, expected_status: int = 200, precise_status_required: bool = False, requires_json: bool = True):
    """This function checks if the response is correct."""
    if (precise_status_required):
        assert (response.status_code == expected_status), \
            f"Unexpected status code: {response.status_code}. It was expected to get {expected_status}."

    else:
        assert ((response.status_code // 100) == (expected_status // 100)), \
            f"Unexpected status code: {response.status_code}. It was expected to get {expected_status // 100}XX."

    if (requires_json):
        content_type = response.headers["Content-Type"]
        content_types = content_type.split(";")
        assert ("application/json" in content_types), \
            f'The API is not responding with JSON, but with "{content_type}".'
    
def compare_lecturers(lecturer: dict, response: dict):
    for lecturer_key, lecturer_value in lecturer.items():
        assert lecturer_key in response, \
            f"The response should contain the key {lecturer_key}, but it doesn't."
        
        # if the key is tags, check if the tags are the same
        if lecturer_key == "tags":
            assert len(response["tags"]) == len(lecturer_value), \
                f"The response should contain {len(lecturer_value)} tags, but it contains {len(response['tags'])}."
            
            # each tag should have a UUID
            for tag in response["tags"]:
                assert "uuid" in tag, \
                    f"The tag should have an uuid, but it doesn't."
                
            # get a list of all the tag names from the response
            response_tag_names = [tag["name"] for tag in response['tags']]
            # get a list of all the tag names from the lecturer
            lecturer_tag_names = [tag["name"] for tag in lecturer_value]

            for tag in lecturer_tag_names:
                assert tag in response_tag_names, \
                    f"The response should contain the tag {tag}, but it doesn't."
        elif lecturer_key == "contact":
            for contact_key, contact_value in lecturer_value.items():
                assert contact_key in response["contact"], \
                    f"The response should contain the key {contact_key} in contact, but it doesn't."
                if contact_key == "telephone_numbers":
                    assert len(response["contact"]["telephone_numbers"]) == len(contact_value), \
                        f"The response should contain {len(contact_value)} telephone numbers, but it contains {len(response['contact']['telephone_numbers'])}."
                elif contact_key == "emails":
                    assert len(response["contact"]["emails"]) == len(contact_value), \
                        f"The response should contain {len(contact_value)} emails, but it contains {len(response['contact']['emails'])}."
                else:
                    assert response["contact"][contact_key] == contact_value, \
                        f"The response should contain the value {contact_value} for the key {contact_key} in contact, but it doesn't."
        else:
            assert response[lecturer_key] == lecturer_value, \
                f"The response should contain the value {lecturer_value} for the key {lecturer_key}, but it doesn't."

def test_basic_post(requestSession: requests.Session, url: str):
    """This test checks the POST route on the API"""
    full_url = urljoin(url, "/api/lecturers")
    lecturer = get_random_lecturer()
    response = requestSession.post(full_url, json=lecturer)
    common_check(response, 200)
    response_json = parse_response(response)
    compare_lecturers(lecturer, response_json)
    check_uuid(response_json)        
    
@pytest.mark.depends(on=[test_basic_post.__name__])
def test_basic_get(requestSession: requests.Session, url: str):
    """This test checks the GET route on the API"""
    full_url = urljoin(url, "/api/lecturers")

    # first push a lecturer to the API
    lecturer = get_random_lecturer()
    response = requestSession.post(full_url, json=lecturer)
    common_check(response, 200)
    searched_uuid = response.json()["uuid"]
    path = "/api/lecturers/" + searched_uuid

    # then get the lecturer from the API
    details_url = urljoin(url, path)
    response = requestSession.get(details_url)
    common_check(response, 200)
    response_json = parse_response(response)
    compare_lecturers(lecturer, response_json)
    check_uuid(response_json, searched_uuid)

@pytest.mark.depends(on=[test_basic_post.__name__])
def test_basic_delete(requestSession: requests.Session, url: str):
    """This test checks the DELETE route on the API"""
    full_url = urljoin(url, "/api/lecturers")

    # first push a lecturer to the API
    lecturer = get_random_lecturer()
    response = requestSession.post(full_url, json=lecturer)
    common_check(response, 200)
    path = "/api/lecturers/" + response.json()["uuid"]

    # then delete the lecturer from the API
    details_url = urljoin(url, path)
    response = requestSession.delete(details_url)
    common_check(response, 200, requires_json=False)

    # then get the lecturer from the API
    details_url = urljoin(url, path)
    response = requestSession.get(details_url)
    common_check(response, 404, precise_status_required=True, requires_json=False)

@pytest.mark.depends(on=[test_basic_post.__name__])
def test_basic_put(requestSession: requests.Session, url: str):
    """This test checks the PUT route on the API"""
    full_url = urljoin(url, "/api/lecturers")

    # first push a lecturer to the API
    lecturer = get_random_lecturer()
    response = requestSession.post(full_url, json=lecturer)
    common_check(response, 200)
    path = "/api/lecturers/" + response.json()["uuid"]

    # then update the lecturer from the API
    lecturer = get_random_lecturer()
    # delete the field title_before
    del lecturer["title_before"]
    details_url = urljoin(url, path)
    response = requestSession.put(details_url, json=lecturer)
    common_check(response, 200)

    # check if the response contains the correct data
    response_json = parse_response(response)
    
    # check if the response contains the correct data
    compare_lecturers(lecturer, response_json)

@pytest.mark.depends(on=[test_basic_post.__name__])
def test_basic_get_all(requestSession: requests.Session, url: str):
    """This test checks the GET route on the API"""
    full_url = urljoin(url, "/api/lecturers")

    # first push a lecturer to the API
    lecturer = get_random_lecturer()
    response = requestSession.post(full_url, json=lecturer)
    common_check(response, 200)

    searched_uuid = response.json()["uuid"]

    # then get all lecturers from the API
    response = requestSession.get(full_url)
    common_check(response, 200)

    # check if the response contains the correct data
    response_json = parse_response(response, list)
    
    # check if the response contains the lecturer we pushed
    found = False
    for res_lec in response_json:
        assert isinstance(res_lec, dict), \
            f"The response should contain an object, but it contains {type(res_lec)}."
        check_uuid(res_lec)
        if res_lec["uuid"] == searched_uuid:
            compare_lecturers(lecturer, res_lec)
            found = True

    assert found, \
        f"The response should contain the lecturer with uuid {searched_uuid}, but it doesn't."
    
@pytest.mark.depends(on=[test_basic_post.__name__])
def test_advanced_post(requestSession: requests.Session, url: str):
    """Check some of the edge cases of the POST route on the API"""
    full_url = urljoin(url, "/api/lecturers")

    # first try to send some empty arrays
    lecturer = get_random_lecturer()
    lecturer["tags"] = []
    response = requestSession.post(full_url, json=lecturer)
    common_check(response, 200)
    response_json = response.json()
    assert isinstance(response_json, dict), \
        f"The response should contain an object, but it contains {type(response_json)}."
    compare_lecturers(lecturer, response_json)
    check_uuid(response_json)

    # then try to send some empty strings
    lecturer = get_random_lecturer()
    lecturer["title_before"] = ""
    lecturer["middle_name"] = ""
    lecturer["title_after"] = ""
    lecturer["location"] = ""
    lecturer["claim"] = ""
    response = requestSession.post(full_url, json=lecturer)
    common_check(response, 200)
    response_json = response.json()
    assert isinstance(response_json, dict), \
        f"The response should contain an object, but it contains {type(response_json)}."
    compare_lecturers(lecturer, response_json)
    check_uuid(response_json)

    # then try to send some nulls
    lecturer = get_random_lecturer()
    lecturer["title_before"] = None
    lecturer["middle_name"] = None
    lecturer["title_after"] = None
    lecturer["location"] = None
    lecturer["claim"] = None
    response = requestSession.post(full_url, json=lecturer)
    common_check(response, 200)
    response_json = parse_response(response)
    compare_lecturers(lecturer, response_json)
    check_uuid(response_json)

    # then try to send undefined fields
    lecturer = get_random_lecturer()
    del lecturer["title_before"]
    del lecturer["middle_name"]
    del lecturer["title_after"]
    del lecturer["location"]
    del lecturer["claim"]
    response = requestSession.post(full_url, json=lecturer)
    common_check(response, 200)
    response_json = parse_response(response)
    compare_lecturers(lecturer, response_json)
    check_uuid(response_json)

    # then try to send some nulls in mandatory fields
    lecturer = get_random_lecturer()
    lecturer["first_name"] = None
    lecturer["last_name"] = None
    response = requestSession.post(full_url, json=lecturer)
    common_check(response, 400)

@pytest.mark.depends(on=[test_basic_get.__name__])
def test_advanced_get(requestSession: requests.Session, url: str):
    """Check some of the edge cases of the GET route on the API"""
    full_url = urljoin(url, "/api/lecturers")

    # first push a lecturer to the API
    lecturer = get_random_lecturer()
    response = requestSession.post(full_url, json=lecturer)
    common_check(response, 200)
    searched_uuid = response.json()["uuid"]

    # then get the lecturer from the API
    details_url = urljoin(url, "/api/lecturers/" + searched_uuid)
    response = requestSession.get(details_url)
    common_check(response, 200)
    response_json = parse_response(response)
    compare_lecturers(lecturer, response_json)
    check_uuid(response_json, searched_uuid)

    # then try to get a non-existent lecturer
    details_url = urljoin(url, "/api/lecturers/" + str(uuid.uuid4()))
    response = requestSession.get(details_url)
    common_check(response, 404)

@pytest.mark.depends(on=[test_basic_delete.__name__])
def test_advanced_delete(requestSession: requests.Session, url: str):
    """Check some of the edge cases of the DELETE route on the API"""
    full_url = urljoin(url, "/api/lecturers")

    # first push a lecturer to the API
    lecturer = get_special_lecturer()
    response = requestSession.post(full_url, json=lecturer)
    common_check(response, 200)
    searched_uuid = response.json()["uuid"]

    # then delete the lecturer from the API
    details_url = urljoin(url, "/api/lecturers/" + searched_uuid)
    response = requestSession.delete(details_url)
    common_check(response, 200, requires_json=False)

    # then try to delete the lecturer again
    response = requestSession.delete(details_url)
    common_check(response, 404, precise_status_required=True, requires_json=False)

    # then try to delete a non-existent lecturer
    details_url = urljoin(url, "/api/lecturers/" + str(uuid.uuid4()))
    response = requestSession.delete(details_url)
    common_check(response, 404, precise_status_required=True, requires_json=False)

@pytest.mark.depends(on=[test_basic_put.__name__])
def test_advanced_put(requestSession: requests.Session, url: str):
    """Check some of the edge cases of the PUT route on the API"""
    full_url = urljoin(url, "/api/lecturers")

    # first push a lecturer to the API
    lecturer = get_random_lecturer()
    response = requestSession.post(full_url, json=lecturer)
    common_check(response, 200)
    searched_uuid = response.json()["uuid"]

    # cache the old bio
    old_bio = lecturer["bio"]
    # then update the lecturer from the API
    lecturer = get_random_lecturer()
    # delete the field bio
    del lecturer["bio"]
    details_url = urljoin(url, "/api/lecturers/" + searched_uuid)
    response = requestSession.put(details_url, json=lecturer)
    common_check(response, 200)

    # check if the response contains the correct data
    response_json = parse_response(response)
    
    # check if the new bio is unchanged
    assert response_json["bio"] == old_bio, \
        f"The bio should not have been changed, but it was."

    # then try to update a non-existent lecturer
    lecturer = get_random_lecturer()
    details_url = urljoin(url, "/api/lecturers/" + str(uuid.uuid4()))
    response = requestSession.put(details_url, json=lecturer)
    common_check(response, 404)

@pytest.mark.depends(on=[test_basic_get_all.__name__])
def test_advanced_get_all(requestSession: requests.Session, url: str):
    """Check some of the edge cases of the GET route on the API"""
    full_url = urljoin(url, "/api/lecturers")

    # try to delete all lecturers
    response = requestSession.get(full_url)
    common_check(response, 200)
    response_json = parse_response(response, list)
    for lecturer in response_json:
        details_url = urljoin(url, "/api/lecturers/" + lecturer["uuid"])
        response = requestSession.delete(details_url)
        common_check(response, 200, requires_json=False)
    
    # then try to get all lecturers from the API
    response = requestSession.get(full_url)
    common_check(response, 200)
    response_json = parse_response(response, list)

    # check if the response contains the correct data
    assert len(response_json) == 0, \
        f"The response should contain 0 lecturers, but it contains {len(response_json)}."