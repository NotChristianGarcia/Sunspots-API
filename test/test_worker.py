"""
Author: Christian R. Garcia
Test get_db_data and insures data is returned correctly
Must have api working on the same machine
***Rather old, unfortunately have to get to some final studying.
***Will now only run if API is running as it relies on a database now.

Run with "py.test-3 test_get_db_data.py"
"""
import sys
import os

CODE_DIR = os.path.dirname(__file__)
sys.path.append(CODE_DIR + "/../src/")
print(CODE_DIR + "/../src/")

from get_db_data import get_db_data
CSV_FILE = CODE_DIR + "/../src/sunspots.csv"

def test_list_type_check():
    assert isinstance(get_db_data(CSV_FILE)[1], list)

def test_dict_type_check():
    for line in get_db_data(CSV_FILE)[1]:
        assert isinstance(line, dict)

def test_dict_length_check():
    for line in get_db_data(CSV_FILE)[1]:
        assert len(line) == 3

def test_keys_check():
    for line in get_db_data(CSV_FILE)[1]:
        assert isinstance(line["id"], int)
        assert isinstance(line["year"], int)
        assert isinstance(line["spots"], int)

def test_list_length_check():
    assert len(open(CSV_FILE).readlines()) == len(get_db_data(CSV_FILE)[1])

def test_list_first_and_last_value_check():
    assert int(open(CSV_FILE).readlines()[0][0:4]) == get_db_data(CSV_FILE)[1][0]["year"]
    assert int(open(CSV_FILE).readlines()[-1][0:4]) == get_db_data(CSV_FILE)[1][-1]["year"]


def test_start_no_end_check():
    assert int(open(CSV_FILE).readlines()[60][0:4]) ==\
            get_db_data(CSV_FILE, 1830)[1][0]["year"]
    assert int(open(CSV_FILE).readlines()[-1][0:4]) ==\
            get_db_data(CSV_FILE, 1830)[1][-1]["year"]

def test_end_no_start_check():
    assert int(open(CSV_FILE).readlines()[0][0:4]) ==\
            get_db_data(CSV_FILE, end=1820)[1][0]["year"]
    assert int(open(CSV_FILE).readlines()[50][0:4]) ==\
            get_db_data(CSV_FILE, end=1820)[1][-1]["year"]

def test_start_and_end_check():
    assert int(open(CSV_FILE).readlines()[20][0:4]) ==\
            get_db_data(CSV_FILE, 1790, 1840)[1][0]["year"]
    assert int(open(CSV_FILE).readlines()[70][0:4]) ==\
            get_db_data(CSV_FILE, 1790, 1840)[1][-1]["year"]

def test_start_greater_than_end_check():
    assert get_db_data(CSV_FILE, 1829, 1729)[0] is True

def test_limit_no_offset_check():
    assert int(open(CSV_FILE).readlines()[0][0:4]) ==\
            get_db_data(CSV_FILE, limit=20)[1][0]["year"]
    assert int(open(CSV_FILE).readlines()[19][0:4]) ==\
            get_db_data(CSV_FILE, limit=20)[1][-1]["year"]

def test_offset_no_limit_check():
    assert int(open(CSV_FILE).readlines()[15][0:4]) ==\
            get_db_data(CSV_FILE, offset=15)[1][0]["year"]
    assert int(open(CSV_FILE).readlines()[-1][0:4]) ==\
            get_db_data(CSV_FILE, offset=15)[1][-1]["year"]

def test_limit_and_offset_check():
    assert int(open(CSV_FILE).readlines()[15][0:4]) ==\
            get_db_data(CSV_FILE, limit=20, offset=15)[1][0]["year"]
    assert int(open(CSV_FILE).readlines()[34][0:4]) ==\
            get_db_data(CSV_FILE, limit=20, offset=15)[1][-1]["year"]
