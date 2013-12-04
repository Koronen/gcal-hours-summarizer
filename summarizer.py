from dateutil.parser import parse as parse_datetime
from getpass import getpass

import gdata.calendar.data
import gdata.calendar.client

SOURCE='Google Calendar Hours Summarizer (https://github.com/Koronen/gcal-hours-summarizer)'

username=raw_input('Username: ')
password=getpass('Password: ')
calendarId=raw_input('CalendarID: ')

def main():
    client = gdata.calendar.client.CalendarClient(source=SOURCE)
    client.ClientLogin(username, password, client.source)

    query = gdata.calendar.client.CalendarEventQuery(start_min='2013-11-01',
            start_max='2013-11-30', max_results=150)
    feed = client.GetCalendarEventFeed('https://www.google.com/calendar/feeds/' +
            calendarId + '/private/full', q=query)

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

if __name__ == "__main__":
    main()
