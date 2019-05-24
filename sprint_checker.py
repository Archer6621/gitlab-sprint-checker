import re
import gitlab
import argparse

from datetime import datetime, timedelta

# Globals
DATE_FORMAT = '%Y-%m-%d'
START_DATE = datetime.strptime('2019-05-03', DATE_FORMAT) + timedelta(seconds=49500)  # Friday at 13:45
SPRINT_LENGTH = 2 * 7
GITLAB_HOST = "https://gitlab.ewi.tudelft.nl"

# Arg handling
parser = argparse.ArgumentParser(description='Show gitlab time spent/estimate statistics per sprint.')
parser.add_argument('project_id', metavar='project_id', type=int,
                    help='Project id of the gitlab project, can be found on the project\'s home page at the top.')

parser.add_argument('private_token', metavar='private_token', type=str,
                    help='Private token for gitlab access, generate at your user settings (Settings -> Access Tokens), grant it api access.')

parser.add_argument('sprint_number', metavar='sprint', type=int,
                    help='The sprint count, every sprint is two weeks, sprint 1 starting at 03-05-19 13:45 (on a Friday).')

parser.add_argument('-e', action='store_true', 
                    help='When given, this flag will not divide the issue estimate among the assignees, but rather add the whole value for each of them.')


args = parser.parse_args()

# Download data from gitlab
ewi_gitlab = gitlab.Gitlab(GITLAB_HOST, private_token=args.private_token)
project = ewi_gitlab.projects.get(args.project_id)


# Checks whether the given date is within the i-th sprint
def is_within_sprint(date, start, i, day_offset = 0):
    return start + timedelta(days=(i - 1) * SPRINT_LENGTH + day_offset) < date < start + timedelta(days=i * SPRINT_LENGTH + day_offset)

# Checks whether the given date is before start of the i-th sprint
def is_before_sprint(date, start, i, day_offset = 0):
    return date < start + timedelta(days=(i - 1) * SPRINT_LENGTH + day_offset)

def mean(L):
    return round(sum(L) / len(L))


def std(L):
    return round((sum([l ** 2 for l in L]) / len(L) - mean(L) ** 2) ** 0.5)


def format_seconds(s):
    m = int(s) // 60
    h = m // 60
    m_rem = m % 60
    return "{:2d}h {:2d}m".format(h, m_rem)


# Create member map
members = {}
for member in project.members.all(all=True):
    if member['access_level'] is 30:  # 30 is developer (https://python-gitlab.readthedocs.io/en/stable/gl_objects/groups.html)
        members[member['username']] = {'time_estimate': 0, 'actual_time_spent': 0}

# Iterate over issues
for issue in project.issues.list(all=True):

    # Skip if the issue was closed in the previous sprint
    if issue.state == 'closed':
        issue_close_date = datetime.strptime(issue.closed_at.split("T")[0], DATE_FORMAT)
        if is_within_sprint(issue_close_date, START_DATE, args.sprint_number - 1):
            continue

    # Only add estimate if the issue was created before the next sprint, before the new planning (hence the given offset argument -1)
    issue_date = datetime.strptime(issue.created_at.split("T")[0], DATE_FORMAT)
    if is_before_sprint(issue_date, START_DATE, args.sprint_number + 1, -1):
        for assignee in issue.assignees:
            if args.e:
                members[assignee['username']]['time_estimate'] += issue.attributes['time_stats']['time_estimate']
            else:
                members[assignee['username']]['time_estimate'] += (issue.attributes['time_stats']['time_estimate'] / len(issue.assignees))

    # Iterate over issue notes, since they contain the "added .... of time spent" messages
    notes = issue.notes.list()
    for note in notes:

        # Extract note date
        note_date = datetime.strptime(note.created_at.split("T")[0], DATE_FORMAT)

        # Extract time spent info from note bodies
        if re.search(r'added .* of time spent at', note.body):
            h_string = re.search(r'\b[0-9]{1,3}h\b', note.body)
            m_string = re.search(r'\b[0-9]{1,3}m\b', note.body)
            s_string = re.search(r'\b[0-9]{1,3}s\b', note.body)
            time_map = {s_string: 1, m_string: 60, h_string: 3600}

            time = 0
            for t in time_map:
                if t is not None:
                    try:
                        # If the note was made during the current sprint, we increment the time spent
                        if is_within_sprint(note_date, START_DATE, args.sprint_number):
                            time += time_map[t] * int(t.group(0)[:-1])
                        # If it was made before, we subtract from the estimate
                        elif is_before_sprint(note_date, START_DATE, args.sprint_number):
                            members[note.author['username']]['time_estimate'] -= time_map[t] * int(t.group(0)[:-1])
                    except:
                        print("Warning: Could not parse time from note")

            members[note.author['username']]['actual_time_spent'] += time

print()
print("Time data for sprint",args.sprint_number,"starting at",START_DATE + timedelta(days=(args.sprint_number-1) * SPRINT_LENGTH))
print()
for member in members:
    f = "{:40s} {:25s} {:25s}"
    print_list = [member] + [t + ": " + format_seconds(members[member][t]) for t in members[member]]
    print(f.format(*print_list))
print()
members_spent = [members[member]['actual_time_spent'] for member in members]
members_estimate = [members[member]['time_estimate'] for member in members]
print("   Mean time spent: ", format_seconds(mean(members_spent)))
print("    Std time spent: ", format_seconds(std(members_spent)))
print("Mean time estimate: ", format_seconds(mean(members_estimate)))
print(" Std time estimate: ", format_seconds(std(members_estimate)))
print()
input("Press a key to continue...")
