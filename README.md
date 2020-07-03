# sw-code-challenge

## Overview
This repository contains documentation and solution artifacts for a Secureworks software code challenge. The documentation can be found in doc and the program artifacts are located in py.

## Documentation
For a description of the problem statement see doc/code-challenge.pdf, which describes the existence of an agent along with some of its behavor. The agent is the target for automated testing.

In the same directory you will alson find test-plan.odt which summarizes test goals and the solution.

## Automated Testing Artifacts
py/stma_test contains three python scripts:
- load_gen.py
- process_results.py
- tp.py

The approach for testing the agent involves two steps: 1) generating a known "load" of threat processes designed to trigger a specific response from the agent, and 2) processing the agent's response by grading it against the expected response.

## Requirements
The test automation runs on both Windows and Linux using Python 3. Because on Windows python3 runs as "python" rather than "python3" and because load_gen.py generates the threat load by running tp.py, running on Linux requires symlinking "python" to python3.

%> which python3

/usr/bin/python3

%> cd /usr/bin

%> sudo ln -sv python3 python

%>

## Execution
First, generate the threat load by running load_gen.py. Do so from py/stma_test.

%> python load_gen.py

Being part of a code challenge where much is to be inferred from the problem description, generating a load of tp.py processes by execution of this first step is largely symbolic - no agent is running to observe the process load on the host and if it were it would likely not be triggered by these particular processes. This is an overly simplified approach to running "threat" processes for the sake of the coding challenge. But it also provides an opportunity to create an expected agent response based upon the number of times tp.py runs and for each run how long it runs. If you change the number of times load_gen.py runs tp.py you alter the contents of the resulting file load_manifest.json.

Second, execute process_results.py to validate the resulting agent response against the expected response in load_manifest.json.

%> cp load_manifest.json agent.json

%> python process_results.json load_manifest.json agent.json

This is really step 2a and 2b. Because there is no agent in this challenge, we synthesize the agent's output by copying the expected output. Once this is done you must execute process_results.json with two arguments: the expected output and the actual output. If executed as above, you should see all successful test cases. The first is a simple (and general) evaluation of threat process counts. The remainder represents a record-by-record comparison keyed off of the PID for each execution of tp.py.

Play with this by creating various copies of agent.json. Leave one unchanged (it should pass all test cases) and update the others in various ways, such as:
- removing a record
- adding a record
- changing a record (e.g. changing a pid or count)

## Future Work
process_results.json should be modified to produce junit output. This would make it very Jenkins-friendly and is an essential step for full automation of the testing suggested by this challenge.

The programs should be more prameterized - expanded use of command-line arguments would make each program more usable. Use of these tools in their current form would make it clear what additional command line arguments would be helpful.

Enhanced argument validation would be worthwhile.