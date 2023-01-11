from datetime import datetime

from orgparse.date import OrgDate


class Valid:
    """Used to validate agenda item: valid.org."""

    heading: str = 'Meeting'

    time_stamps: list = [OrgDate(datetime(2023, 1, 1, 1, 0),
                                 datetime(2023, 1, 1, 2, 0))]
    scheduled: OrgDate = OrgDate(None)
    deadline: OrgDate = OrgDate(None)
    properties: dict = {'ID': '123',
                        'CALENDAR': 'outlook',
                        "LOCATION": 'Somewhere',
                        "ORGANIZER": 'Someone (someone@outlook.com)',
                        "URL": 'www.test.com'}
    body: str = "  <2023-01-01 Sun 01:00-02:00>\n\n  Hello,\n\n  Lets have a meeting.\n\n  Regards,\n\n\n  Someone"
    args: list = [heading, time_stamps, scheduled, deadline, properties, body]
