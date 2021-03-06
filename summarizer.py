#!/usr/bin/env python

from os import environ as ENV
from os.path import exists as file_exists
from argparse import ArgumentParser
from dateutil.parser import parse as parse_datetime
from getpass import getpass
from itertools import groupby

import gdata.calendar.data
import gdata.calendar.client

SOURCE='Google Calendar Hours Summarizer (https://github.com/Koronen/gcal-hours-summarizer)'

def main():
    conf = load_configuration()
    client = build_client(conf.username, conf.password)
    feed = client.GetCalendarEventFeed(calendar_url(conf.calendar_id),
        q=build_query(conf.start_min, conf.start_max))

    def entry_to_event_tuple(entry):
        title = entry.title.text
        description = entry.content.text or '-'
        description = description.splitlines()[0]
        starts_at = parse_datetime(entry.when[0].start)
        ends_at = parse_datetime(entry.when[0].end)
        duration = (ends_at - starts_at).seconds / 3600.0
        return (title, description, duration)

    events = sorted(map(entry_to_event_tuple, feed.entry))

    def get_duration(events):
        return sum(map(lambda x: x[-1], events))

    for title, ebt in groupby(events, key=lambda x: x[0]):
        events_by_title = list(ebt)
        print "%s: %.2f h" % (title, get_duration(events_by_title))

        for description, ebd in groupby(events_by_title, key=lambda x: x[1]):
            events_by_description = list(ebd)
            print "    %s: %.2f h" % (description, get_duration(events_by_description))

    total_hours = get_duration(events)
    full_time_hours = 168
    print "----"
    print "Total: %.2f h" % (total_hours)
    if conf.hourly_rate:
        print "Gross: %.2f SEK" % (total_hours*conf.hourly_rate)
        if conf.tax_rate:
            print "Net:   %.2f SEK" % (total_hours*conf.hourly_rate*(1.0-conf.tax_rate))
    print "Perc.: %.1f%%" % (100.0*total_hours/full_time_hours)

def load_configuration():
    read_dotenv('.env')

    parser = ArgumentParser(description='Summarizes durations of calendar events.')
    parser.add_argument('-u', '--username', type=str, help='set username to use for login')
    parser.add_argument('-p', '--password', type=str, help='set password to use for login')
    parser.add_argument('-c', '--calendar', type=str, dest='calendar_id', help='set calendar to use (CalendarID)')
    parser.add_argument('-r', '--hourly-rate', type=float, help='set hourly rate to use for payment calculations')
    parser.add_argument('-t', '--tax-rate', type=float, help='set tax rate to use for payment calculations')
    parser.add_argument('start_min', metavar='START_MIN', type=parse_datetime,
            help='the beginning of the time range (ISO 8601, inclusive)',
            default='2014-01-01')
    parser.add_argument('start_max', metavar='START_MAX', type=parse_datetime,
            help='the end of the time range (ISO 8601, exclusive)')
    args = parser.parse_args()

    def env(name):
        return ENV.get(name, None)

    if not args.username:
       args.username = env('USERNAME')
    if not args.username:
        args.username = raw_input('Username: ')

    if not args.password:
       args.password = env('PASSWORD')
    if not args.password:
        args.password = getpass('Password: ')

    if not args.calendar_id:
       args.calendar_id = env('CALENDARID')
    if not args.calendar_id:
        args.calendar_id = raw_input('CalendarID: ')

    if not args.hourly_rate and env('HOURLY_RATE'):
        args.hourly_rate = float(env('HOURLY_RATE'))

    if not args.tax_rate and env('TAX_RATE'):
        args.tax_rate = float(env('TAX_RATE'))

    return args

def read_dotenv(dotenv):
    if file_exists(dotenv):
        for k, v in parse_dotenv(dotenv):
            ENV.setdefault(k, v)

def parse_dotenv(dotenv):
    for line in open(dotenv):
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        v = v.strip("'").strip('"')
        yield k, v

def build_client(username, password):
    client = gdata.calendar.client.CalendarClient(source=SOURCE)
    client.ClientLogin(username, password, client.source)
    return client

def calendar_url(calendar_id):
    return 'https://www.google.com/calendar/feeds/' + calendar_id + '/private/full'

def build_query(start_min, start_max):
    return gdata.calendar.client.CalendarEventQuery(
        start_min=start_min.isoformat(), start_max=start_max.isoformat(), max_results=150)

if __name__ == "__main__":
    main()
