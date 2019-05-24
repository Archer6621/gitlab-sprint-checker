# Gitlab Sprint Checker
Tool to check estimated and spent hours of developers in some gitlab repository via an access token. The spent hours are checked by reading the `/spent` notes, given that developers use this feature. The estimated hours are a bit more tricky to get right since they are per issue and certain issues may or may not persist across sprints. (explanation of what it does will follow shortly)

The current version is adapted for use on TU Delft, but this will be generalized soon(tm).

## Dependencies
- Python 3
- Gitlab Python API

## Instructions (Windows)
- Install Python 3: https://www.python.org/downloads/
- Run the following command to install the Gitlab Python API: `pip install python-gitlab`
- Run `python sprint_checker.py -h` for further usage

The tool requires a Gitlab access token, which you can create at your user settings.
