#!/usr/bin/env python3
"""
This module evaluates an agent's threat reporting. It does so by comparing it's
output to a manifest describing the threat load executed in the presence of the
agent.

Example:
    python process_results.py load_manifest.json agent_response.json

    where load_manifest.json is created by load_gen.py
    and agent_response.json is created by the agent under test

To test process_results.py (we test our test applications, right?...)
1) run load_gen.py
2) create agent_response.json by copying load_manifest.json
3) create variations of agent_response.json (add/remove/edit one or more records)
4) run process_results.py passing in the various "detections" and evaluate the various results
"""
import json
import sys


def dictionary_from_json_file(_json_file):
    """
    Given the name of a file containing json-encoded data, this function
    produces the parsed version of the data in the form of a dictionary.

    :param _json_file: the filename containing the data
    :return (dictionary): the parsed data

    todo: add error handling
    """
    with open(_json_file) as _f:
        _dict = json.load(_f)
    return _dict


def find_first_match(_list, _item):
    """
    Given a _list of items, find the first item matching _item and return it.

    :param _list: list of items
    :param _item: an item to match in the list of items
    :return (dictionary): the matching item from _list
    """
    for _list_item in _list:
        if _item["pid"] == _list_item["pid"]:
            return _list_item
    return None


def equivalent_dicts(_a, _b):
    """
    Evaluate the equivalency of two dictionaries. This is a key/value driven
    comparison which is driven by the first (primary) dictionary. To fully
    establish equivalency between two dictionaries one would use this
    function twice, swapping the order of dictionaries between uses.

    Example:
        _equivalent = equivalent_dicts(a, b) and equivalent_dicts(b, a)

    :param _a: the primary dictionary
    :param _b: the secondary dictionary
    :return (boolean): True if equivalent, false otherwise
    """
    for _key in _a.keys():
        if _a[_key] != _b[_key]:
            return False
    return True


def process_results(_load_manifest, _stma_report):
    """
    Given _load_manifest (the expected agent response) and _stma_report (the
    actual response), evaluate the agent's response and produce a set of pass-
    fail grades for the test execution.

    :param _load_manifest: the actual threat load executed in the presence of the agent
    :param _stma_report:  the agent's response to the threat load
    :return: junit-encoded test results

    todo: implement the junit-packaging of the results
    """
    _junit_results = []
    # the first "test" is that the two lists should have the same number of items
    if len(_load_manifest) == len(_stma_report):
        print("result count test: pass")
    else:
        print("result count test: fail")

    # for the rest, each item in the load manifest equates to a test
    for _load_item in _load_manifest:
        _pass = True
        # get its associated entry from the _stma_report
        _stma_item = find_first_match(_stma_report, _load_item)
        if _stma_item is None:
            _pass = False
            print("test " + str(_load_item) + ": fail due to missing stma result")
        else:
            # verify details reported by stma
            _pass = equivalent_dicts(_load_item, _stma_item) and\
                    equivalent_dicts(_stma_item, _load_item)
            if not _pass:
                print("test " + str(_load_item) + ": fail due to mismatching result")
        print("test " + str(_load_item) + ": " + str(_pass))

    return _junit_results


if __name__ == "__main__":
    load_manifest = dictionary_from_json_file(sys.argv[1])
    stma_report = dictionary_from_json_file(sys.argv[2])
    junit_results = process_results(load_manifest, stma_report)
