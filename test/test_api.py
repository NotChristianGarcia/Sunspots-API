"""
Author: Christian R. Garcia
Tester for API server. API must be running to test.
Redesigned, but not really renamed, checks a variety of stuff.
Function names give a good sense of what's happening throughout this tester
because I don't want to write docstrings.

Insure flask API server is running then run with "py.test-3 test_api.py"
"""
import os
import json
import requests as r
import pytest

CODE_DIR = os.path.dirname(__file__)
CSV_FILE = CODE_DIR + "/../src/sunspots.csv"
BASE_URL = "http://localhost:5000"


def get_from_server(extraURL):
    req = r.get("{}{}".format(BASE_URL, extraURL))
    return req

def post_to_server(extraURL, data):
    req = r.post("{}{}, {}".format(BASE_URL, extraURL, json.dumps(data)))
    return req


# Checking GET /spots with no input
@pytest.fixture(scope="module")
def section_one():
    return get_from_server("/spots")

def test_a1CheckStatus(section_one):
    assert section_one.status_code == 200

def test_b1CheckJSON(section_one):
    assert section_one.json() is not None

def test_c1CheckList(section_one):
    assert isinstance(section_one.json(), list)

def test_d1CheckDict(section_one):
    assert isinstance(section_one.json()[1], dict)

def test_e1CheckDictLen(section_one):
    assert len(section_one.json()[1]) == 3

def test_f1CheckKeyType(section_one):
    for i in section_one.json():
        assert isinstance(i["id"], int)
        assert isinstance(i["year"], int)
        assert isinstance(i["spots"], int)

def test_g1CheckListLen(section_one):
    assert len(section_one.json()[:]) == len(open(CSV_FILE).readlines())

def test_f1CheckFirstNLastDict(section_one):
    assert int(open(CSV_FILE).readlines()[0][0:4]) == section_one.json()[0]["year"]
    assert int(open(CSV_FILE).readlines()[-1][0:4]) == section_one.json()[-1]["year"]


# Checking GET /spots with inputs
@pytest.fixture(scope="module", params=[["start=1780&end=1819", 40],
                                        ["start=1780"         , 90],
                                        ["end=1839"           , 70],
                                        ["start=1800&end=1819", 20],
                                        ["limit=10&offset=20" , 10],
                                        ["limit=20"           , 20],
                                        ["offset=20"          , 80]])
def section_two(request):
    return [get_from_server("/spots?{}".format(request.param[0])), request.param[1]]

def test_a2CheckStatus(section_two):
    assert section_two[0].status_code == 200

def test_b2CheckJSON(section_two):
    assert section_two[0].json() is not None

def test_c2CheckList(section_two):
    assert isinstance(section_two[0].json(), list)

#def test_d2CheckListLen(section_two):
#    assert len(section_two[0].json()[:]) == section_two[1]

# Checking GET /spots with incorrect inputs
@pytest.fixture(scope="module", params=["start=abc",
                                        "end=abc",
                                        "limit=-1",
                                        "offset=-1",
                                        "start=1770&limit=20"])
def section_three(request):
    return get_from_server("/spots?{}".format(request.param))

def test_a3CheckStatus(section_three):
    assert section_three.status_code == 400

def test_b3CheckString(section_three):
    assert isinstance(section_three.json(), list)

def test_c3CheckList(section_three):
    assert section_three.json()[0] is not None


# Checking GET /spots/ids/<id>
@pytest.fixture(scope="module", params=["1", "30", "99"])
def section_four(request):
    return [get_from_server("/spots/ids/{}".format(request.param)), request.param]

def test_a4CheckStatus(section_four):
    assert section_four[0].status_code == 200

def test_b4CheckJSON(section_four):
    assert section_four[0].json() is not None

def test_c4CheckDict(section_four):
    assert isinstance(section_four[0].json(), dict)

def test_d4CheckDictLen(section_four):
    assert len(section_four[0].json()) == 3

def test_e4CheckID(section_four):
    assert section_four[0].json()["id"] == int(section_four[1])


# Checking GET /spots/years/<year>
@pytest.fixture(scope="module", params=["1771", "1834", "1859"])
def section_five(request):
    return [get_from_server("/spots/years/{}".format(request.param)), request.param]

def test_a5CheckStatus(section_five):
    assert section_five[0].status_code == 200

def test_b5CheckJSON(section_five):
    assert section_five[0].json() is not None

def test_c5CheckDict(section_five):
    assert isinstance(section_five[0].json(), dict)

def test_d5CheckDictLen(section_five):
    assert len(section_five[0].json()) == 3

def test_e5CheckID(section_five):
    assert section_five[0].json()["year"] == int(section_five[1])


# Checking POST /spots
@pytest.fixture(scope="module", params=[{"year": 1800, "spots": 67},
                                        {"year": 2016, "spots": 231},
                                        {"year": 2036, "spots": 321},
                                        {"year": 2630, "spots": 4313},
                                        {"year": 640, "spots": 22}])
def section_six(request):
    return post_to_server("/spots", request.param)

def get_spots():
    return get_from_server("/spots")

def test_a6CheckStatus(section_six):
    assert section_six.status_code == 200

def test_b6CheckJSON(section_six):
    assert isinstance(section_six.json(), str)
