# Gitlab Sprint Checker
Tool to check estimated and spent hours of developers in some gitlab repository via an access token. 

The spent hours are checked by reading the `/spent` notes, given that developers use this feature. The estimated hours are a bit more tricky to get right since they are per issue and certain issues may or may not persist across sprints. So a couple of things are done in order to try to get estimates that are somewhat sensible:
- Estimated time per developer is obtained by dividing the time estimate of an issue over the assignees
- Issues closed in the previous sprint are skipped entirely: only issues created during the current or previous sprints are considered for both time spent and time estimated
- For issues created during previous sprints, time spent during those sprints is subtracted from the total estimate of that developer for the current sprint, this is done to deal with issues that last several sprints
- NOTE: The estimate may become negative as a result from this, which would indicate that issue estimates are not being updated appropriately by the team over the sprints


The current version is adapted for use on the TU Delft Software Quality & Testing course, but this will be generalized soon(tm).

## Dependencies
- Python 3
- Gitlab Python API

## Instructions (Windows)
- Install Python 3: https://www.python.org/downloads/
- Run the following command to install the Gitlab Python API: `pip install python-gitlab`
- Run `python sprint_checker.py -h` for further usage

The tool requires a Gitlab access token, which you can create at your user settings.
