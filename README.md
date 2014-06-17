# Google Calendar Hours Summarizer

A small tool that fetches all calendar events in a given time range, groups them
by title and by description and aggregates their duration (in hours).

## Dependencies

This script depends on Python 2.7+ and the Google Data APIs. On Debian
derivatives, these can be installed by running the following command.

    sudo apt-get install -y python python-gdata

## Configuration

This script requires, at minimum, a Google account username (email address), a
Google account password and a Google calendar ID.

The calendar ID can be found by opening Google Calendar, clicking on "Settings",
"Calendars" and your calendar of choise. The Calendar ID is then displayed on
the row "Calendar Address".

If you don't feel like providing these credentials every time you run the
program, some or all of these configuration options can be stored in a file
called `.env` (see `.env.sample` for a template).

## How to run

    python ./summarizer.py [OPTIONS] START_MIN START_MAX

where `START_MIN` and `START_MAX` are ISO 8601 dates or times forming a time
range. Note that `START_MIN` in inclusive and `START_MAX` exclusive.

For further detail, run

    python ./summarizer.py --help
