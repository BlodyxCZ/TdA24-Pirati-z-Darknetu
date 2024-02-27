from icalendar import Calendar, Event

# WIP
def create_icalendar(events):
    cal = Calendar()
    cal.add('prodid', '-//My calendar product//mxm.dk//')  # TODO: Change this
    cal.add('version', '2.0')

    for event in events:
        e = Event()
        e.add('summary', event["summary"])
        e.add('dtstart', event["dtstart"])
        e.add('dtend', event["dtend"])
        e.add('description', event["description"])
        cal.add_component(e)

    return cal.to_ical()
