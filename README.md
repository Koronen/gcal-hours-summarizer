# Google Calendar Hours Summarizer

A small tool that fetches all calendar events in a given month, groups them by
title and aggregates their duration (in hours).

## Dependencies

This script depends on Python 2.7+ and the Google Data APIs. On Debian
derivatives, these can be installed by running the following command.

    sudo apt-get install -y python python-gdata

## Configuration

This script requires, at minimum, a Google account password (email address), a
Google account password and a Google calendar ID.

The calendar ID can be found by opening Google Calendar, clicking on "Settings",
"Calendars" and your calendar of choise. The Calendar ID is then displayed on
the row "Calendar Address".

If you don't feel like providing these credentials every time you run the
program, some or all of these configuration options can be stored in a file
called `.env` (see `.env.sample` for a template).

## How to run

    python ./summarizer.py
