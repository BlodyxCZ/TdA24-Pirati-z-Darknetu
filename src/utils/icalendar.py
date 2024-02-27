from icalendar import Calendar, Event
from datetime import datetime


def generate_icalendar(events: list):
    cal = Calendar()
    cal.add('prodid', '-//Teacher digital Agency//Katalog lektorů//cs-CZ')
    cal.add('version', '2.0')

    for event in events:
        e = Event()
        e.add('summary', "TdA Rezervace")
        e.add('dtstart', datetime.fromisoformat(event["start_date"]))
        e.add('dtend', datetime.fromisoformat(event["end_date"]))
        e.add('description', event["info"])

        cal.add_component(e)

    return cal.to_ical()
