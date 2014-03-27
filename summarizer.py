#!/usr/bin/env python

from os import environ as ENV
from os.path import exists as file_exists
from argparse import ArgumentParser
from dateutil.parser import parse as parse_datetime
from getpass import getpass

import gdata.calendar.data
import gdata.calendar.client

SOURCE='Google Calendar Hours Summarizer (https://github.com/Koronen/gcal-hours-summarizer)'

def main():
    conf = load_configuration()
    client = build_client(conf.username, conf.password)
    feed = client.GetCalendarEventFeed(calendar_url(conf.calendar_id),
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

    for title, duration in sorted(aggregated_hours.items()):
        print "%s: %.2f h" % (title, duration)

    total_hours = sum(aggregated_hours.values())
    full_time_hours = 167
    print "----"
    print "Total: %.2f h" % (total_hours)
    if conf.hourly_rate:
        print "Gross: %.2f SEK" % (total_hours*conf.hourly_rate)
        if conf.tax_rate:
            print "Net:   %.2f SEK" % (total_hours*conf.hourly_rate*(1.0-conf.tax_rate))
    print "Perc.: %.2f%%" % (total_hours/full_time_hours)

def load_configuration():
    read_dotenv('.env')

    parser = ArgumentParser(description='Summarizes durations of calendar events')
    parser.add_argument('-u', '--username', type=str, help='set username to use for login')
    parser.add_argument('-p', '--password', type=str, help='set password to use for login')
    parser.add_argument('-c', '--calendar', type=str, dest='calendar_id', help='set calendar to use (CalendarID)')
    parser.add_argument('-r', '--hourly-rate', type=float, help='set hourly rate to use for payment calculations')
    parser.add_argument('-t', '--tax-rate', type=float, help='set tax rate to use for payment calculations')
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

def build_query():
    return gdata.calendar.client.CalendarEventQuery(start_min='2013-11-01',
            start_max='2013-11-30', max_results=150)

if __name__ == "__main__":
    main()
