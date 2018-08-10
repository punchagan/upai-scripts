#!/usr/bin/env python3
"""Create an iCal file without registration events an exported calendar.

Usage:

    ./update-calendar.py

This will create an iCal file with the new events missing from the Google
Calendar. These events can then be imported by visiting
https://calendar.google.com/calendar/r/settings/export

"""
from __future__ import print_function

import datetime
from os.path import abspath, dirname, join

import arrow
from dateutil import tz
from googleapiclient.discovery import build
from httplib2 import Http
from ics import Calendar
import mock
from oauth2client import file, client, tools
import requests

HERE = dirname(abspath(__file__))
UPAI_EVENT_URL = 'http://indiaultimate.org/calendar/event'
CALENDAR_OUTPUT_PATH = join(HERE, 'upai-events.ical')
# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CALENDAR_ID = 'lm83aeds6cuh0lp3cfv0s42lgs@group.calendar.google.com'
TZINFO = tz.gettz('Asia/Kolkata')


def build_calendar_service():
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    return build('calendar', 'v3', http=creds.authorize(Http()))


def list_google_events():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    service = build_calendar_service()
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=now,
        maxResults=2500,
        singleEvents=True,
        orderBy='startTime',
    ).execute()
    return events_result.get('items', [])


def filter_registration_events(calendar):
    events = [
        event
        for event in calendar.events
        if not event.name.startswith('Registration for')
    ]
    calendar.events = events
    return calendar


def filter_future_events(calendar):
    events = [event for event in calendar.events if event.begin > arrow.now()]
    calendar.events = events
    return calendar


def filter_existing_events(calendar):
    existing_events = list_google_events()
    existing_names = {event['summary'] for event in existing_events}
    events = [
        event for event in calendar.events if event.name not in existing_names
    ]
    if len(events) != len(calendar.events):
        print('These events are already in the calendar: ')
    for event in calendar.events:
        if event.name in existing_names:
            print(event.name, event.begin)
    calendar.events = events
    return calendar


def main():
    c = Calendar(requests.get(UPAI_EVENT_URL).text)
    print('Found {} events in UPAI calendar'.format(len(c.events)))
    filter_registration_events(c)
    print('{} non-registration events'.format(len(c.events)))
    filter_future_events(c)
    print('{} future events'.format(len(c.events)))
    filter_existing_events(c)
    print('{} future events not in Google Calendar'.format(len(c.events)))
    for event in c.events:
        print(event.name, event.begin)
    # HACK: ics seems to write dates in UTC, which causes events to be on the
    # wrong day! So, we patch stuff in `ics` to use our local timezone
    with mock.patch('ics.utils.tzutc', new=TZINFO):
        with open(CALENDAR_OUTPUT_PATH, 'w') as f:
            f.writelines(c)
    print('New events written to calendar: {}'.format(CALENDAR_OUTPUT_PATH))


if __name__ == '__main__':
    import sys

    if '-h' in sys.argv or '--help' in sys.argv:
        print(__doc__)
        sys.exit(0)
    main()
