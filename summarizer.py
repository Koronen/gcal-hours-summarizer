from os import environ as ENV
from argparse import ArgumentParser
from dateutil.parser import parse as parse_datetime
from getpass import getpass

import gdata.calendar.data
import gdata.calendar.client

SOURCE='Google Calendar Hours Summarizer (https://github.com/Koronen/gcal-hours-summarizer)'

def main():
    username, password, calendar_id = load_configuration()
    client = build_client(username, password)
    feed = client.GetCalendarEventFeed(calendar_url(calendar_id),
            q=build_query())

    def entry_to_event_tuple(entry):
        title = entry.title.text
        starts_at = parse_datetime(entry.when[0].start)
        ends_at = parse_datetime(entry.when[0].end)
        duration = (ends_at - starts_at).seconds / 3600.0
        return (title, duration)

    events = map(entry_to_event_tuple, feed.entry)

    def aggregate_hours(prev, curr):
        title, duration = curr[0], curr[1]
        try:
            prev[title] += duration
        except KeyError:
            prev[title] = duration
        return prev

    aggregated_hours = reduce(aggregate_hours, events, {})

    for title, duration in aggregated_hours.items():
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

def build_client(username, password):
    client = gdata.calendar.client.CalendarClient(source=SOURCE)
    client.ClientLogin(username, password, client.source)
    return client

def calendar_url(calendar_id):
    return 'https://www.google.com/calendar/feeds/' + calendar_id + '/private/full'

def build_query():
    return gdata.calendar.client.CalendarEventQuery(start_min='2013-11-01',
            start_max='2013-11-30', max_results=150)

if __name__ == "__main__":
    main()
