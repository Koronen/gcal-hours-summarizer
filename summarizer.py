from os import environ as ENV
from argparse import ArgumentParser
from dateutil.parser import parse as parse_datetime
from getpass import getpass

import gdata.calendar.data
import gdata.calendar.client

SOURCE='Google Calendar Hours Summarizer (https://github.com/Koronen/gcal-hours-summarizer)'

def main():
    username, password, calendar_id = load_configuration()

    client = gdata.calendar.client.CalendarClient(source=SOURCE)
    client.ClientLogin(username, password, client.source)

    query = gdata.calendar.client.CalendarEventQuery(start_min='2013-11-01',
            start_max='2013-11-30', max_results=150)
    feed = client.GetCalendarEventFeed('https://www.google.com/calendar/feeds/' +
            calendar_id + '/private/full', q=query)

    hours = {}
    for event in feed.entry:
        title = event.title.text
        starts_at = parse_datetime(event.when[0].start)
        ends_at = parse_datetime(event.when[0].end)
        duration = (ends_at - starts_at).seconds / 3600.0
        try:
            hours[title] += duration
        except KeyError:
            hours[title] = duration

    for title, duration in hours.items():
        print "%s: %.2f" % (title, duration)

def load_configuration():
    parser = build_argument_parser()
    args = parser.parse_args()

    username = ENV.get('USERNAME', None)
    if args.username:
        username = args.username
    if not username:
        username = raw_input('Username: ')

    password = ENV.get('PASSWORD', None)
    if args.password:
        password = args.password
    if not password:
        password = getpass('Password: ')

    calendar = ENV.get('CALENDAR', None)
    if args.calendar:
        calendar = args.calendar
    if not calendar:
        calendar = raw_input('CalendarID: ')

    return username, password, calendar

def build_argument_parser():
    parser = ArgumentParser(description='Summarizes durations of calendar events')
    parser.add_argument('-u', '--username', type=str, help='set username to use for login')
    parser.add_argument('-p', '--password', type=str, help='set password to use for login')
    parser.add_argument('-c', '--calendar', type=str, help='set calendar to use')
    return parser

if __name__ == "__main__":
    main()
