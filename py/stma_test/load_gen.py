#!/usr/bin/env python3

"""

This module executes a set of processes each of which is considered to be of a
signature which should be sensed and reported by the STMA agent. It launches
the set of processes serially but asynchronously so that they run concurrently.

Once the last of the processes completes, this module generates a manifest of
executed processes to a file. This manifest represents the official record of
what the STMA agent is expected to have sensed and reported.

Example:
    python load_gen.py

Todo:
    * make the load descriptor configurable at runtime, most likely via some
      kind of command-line argument(s)

"""

import json
import subprocess
import time


def create_load_descriptor():
    """
    Create a list of tuples. Each item in the tuple describes an execution of
    tp.py to be performed. The tuple format is:

        (<pre-run-delay>, <run-duration>, <expected-sensor-detection-count>, <tag>)

    where:

        pre-run-delay and run-duration are in seconds

        expected-sensor-detection-count begins at 1 and increments every 60 seconds
        that the tp.py process executes

        tag is passed to tp.py as a command-line argument which ensure uniqueness
        of the process within the OS's table of active processes. The tag itself is
        of the form <effective-delay>-<duration> where "effective-delay" is the
        accumulated delay for that launch plus all of the previous process launch
        delays.

    :return (list of tuples): load descriptor
    """

    return [(0, 61, 2, "0-61"),
            (10, 59, 1, "10-59"),
            (20, 1, 1, "30-1")]


def start_tp(_duration, _tag):
    """
    Launches tp.py and returns a process object.

    :param _duration: how long in seconds the process will run
    :param _tag: a unique string passed as an argument
    :return: process object

    """
    return subprocess.Popen(['python', 'tp.py', str(_duration), _tag],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True)


def finish_tp(_process_record):
    """
    Waits for the process identified in the process record to complete. This
    function returns a tuple describing the completed process. The tuple is of
    the formm:

    (<pid>, <return-code>, <strout>, <sterr>, <program-file>, <count>)

    :param _process_record: a tuple containing the process's program, its
           process object, and the duration-based count
    :return: the process's run descriptor tuple
    """

    _exe = _process_record[0]
    _process = _process_record[1]
    _count = _process_record[2]

    _pid = _process.pid
    while True:
        _rc = _process.poll()
        if _rc is not None:
            _pout = ", ".join(_process.stdout.readlines()).rstrip()
            _perr = ", ".join(_process.stderr.readlines()).rstrip()
            break
    _presult = (_pid, _rc, _pout, _perr, _exe, _count)
    return _presult


def execute_load(_load_descriptor):
    """
    Execute the process load described by the load descriptor and return a list
    of descriptors documenting each execution.

    This function runs tp.py once for each item in the load descriptor. It does
    so in two phases: a launch phase and a completion phase. In the launch
    phase this function iterates over the list launching a process for each
    item and adding to a list of active processes. The active process list is
    used in the completion phase to gather each process upon its completion.

    Note that while the order of launching and gathering follow the order of
    items in the load descriptor, the actual order of completion varies
    according to when each process launches and how long it runs. This is fine.
    The only requirement (other than faithfully executing the described load)
    is to allow all processes to complete before completion of this function.

    :param _load_descriptor:
    :return: list of process run descriptors

    """
    _procs = []
    for _load_item in _load_descriptor:
        _sleep_time = _load_item[0]
        _run_duration = _load_item[1]
        _count = _load_item[2]
        _tag = _load_item[3]
        time.sleep(_sleep_time)
        _process = start_tp(_run_duration, _tag)
        _process_record = ("tp.py", _process, _count)
        _procs.append(_process_record)

    _load_results = []
    for _proc in _procs:
        _load_results.append(finish_tp(_proc))

    return _load_results


def create_load_manifest(_load_results, _fname):
    """
    Create a json-encoded description of the executed process load.

    :param _load_results: the list of process execution details
    :param _fname: the filename to contain the json-encoded documentation
    :return:
    """

    # assemble the data to be written to the new manifest file
    _manifest_data = []
    for _load_result in _load_results:
        _manifest_data.append({"pid":   _load_result[0],
                               "rc":    _load_result[1],
                               "tag":   _load_result[2],
                               "exe":   _load_result[4],
                               "count": _load_result[5]})

    # create the manifest file from the assembled data
    with open(_fname, "w") as _manifest_file:
        json.dump(_manifest_data, _manifest_file)
        _manifest_file.close()


if __name__ == "__main__":
    load_descriptor = create_load_descriptor()
    load_results = execute_load(load_descriptor)
    create_load_manifest(load_results, "load_manifest.json")
