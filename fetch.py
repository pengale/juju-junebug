#!/usr/bin/env python3

#
# Quick script to fetch recent Juju bug activity.
#
# TODO: generalize and share.
# TODO: login non-anonymously
#

# Launchpad lib help docs: https://help.launchpad.net/API/launchpadlib

import os
import sys
from datetime import datetime, timezone

from launchpadlib.launchpad import Launchpad

HOME = os.path.expanduser("~")
NOW = datetime.now(timezone.utc)  # Timezone aware datetime object
CACHEDIR = f"{HOME}/.launchpadlib/cache/"
OUTPUT_DIR = f"{HOME}/Areas/Juju/"
NEW_BUGS = f"{OUTPUT_DIR}/bugs-new.csv"
FIELD_BUGS = f"{OUTPUT_DIR}/bugs-field.csv"


def bug_age(bug):
    '''
    Try to determine a bug's age.

    '''
    end = bug.date_closed or NOW
    start = bug.date_incomplete or bug.date_created

    delta = end - start

    return delta.days


def bug_age_new(bug):
    '''
    Determine the age of a bug in new status.

    '''
    last_activity = bug.bug.activity.entries[-1]["datechanged"]

    end = NOW
    start = datetime.fromisoformat(last_activity)

    delta = end - start

    return delta.days



def fetch_bugs(project, bug_age=bug_age, **search_params):
    '''
    Go and get a list of bugs. Interface documented at
    https://launchpad.net/+apidoc/1.0.html

    @param project: search this project for bugs matching the **search_params

    @param bug_age: function to determine a bug's age. Can be
      overridden with any function that takes a launchpad api bug
      object as its only argument.

    '''
    total_days = 0
    longest = ("-", "-")
    shortest = ("-", "-")

    bugs = project.searchTasks(**search_params)
    num = len(bugs)

    for bug in bugs:
        print(bug)
        days = bug_age(bug)
        total_days += days

        if longest[0] == "-" or days > longest[0]:
            bug_id = bug.self_link.split('/')[-1]
            longest = (days, bug_id)
        if shortest[0] == "-" or days < shortest[0]:
            bug_id = bug.self_link.split('/')[-1]
            shortest = (days, bug_id)

    avg_days = int(total_days / num) if num > 0 else "-"

    return [num, avg_days, longest[0], longest[1], shortest[0], shortest[1]]


def field_report(launchpad, project):
    '''
    Collect all bugs matching the field-high, field-critical or field-medium tag.

    TODO: only report bugs currently open, or closed this year.

    '''
    data = []
    date =  f'{NOW.year}/{NOW.month}/{NOW.day}'

    for team_name in ['field-critical', 'field-high', 'field-medium']:
        team = launchpad.people(team_name)
        bugs = ','.join(str(f) for f in fetch_bugs(project, bug_subscriber=team.self_link))
        data.append(f'{date},{team_name},{bugs}')

    return FIELD_BUGS, data


def new_report(launchpad, project):
    '''
    Collect stats on all new bugs.

    '''
    date =  f'{NOW.year}/{NOW.month}/{NOW.day}'
    bugs = ','.join(str(f) for f in fetch_bugs(
        project, bug_age=bug_age_new, status=['New']))
    return NEW_BUGS, [f'{date},{bugs}']


def test_report(launchpad, project):
    '''
    Space for hacking on test script stuffs.

    '''

    bugs = project.searchTasks(status=['New'])
    bug = bugs[0]
    for field in bug.lp_attributes:
        print(f'{field}: {getattr(bug, field)}')

    assert bug.date_in_progress is None


def print_report(filename, data):
    '''
    Output a report

    '''
    with open(filename, 'a') as file_:
        for line in data:
            file_.write(f'\n{line}')


def main():
    '''
    Entry point.

    '''
    launchpad = Launchpad.login_anonymously('petevg testing', 'production',
                                            CACHEDIR, version='devel')
    project = launchpad.projects('juju')

    if '--field' in sys.argv or '-f' in sys.argv:
        print_report(*field_report(launchpad, project))

    if '--new' in sys.argv or '-f' in sys.argv:
        print_report(*new_report(launchpad, project))

    if '--test' in sys.argv:
        test_report(launchpad, project)


if __name__ == '__main__':
    main()
