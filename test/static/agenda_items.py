from datetime import datetime

from orgparse.date import OrgDate


class OrgArguments:
    """TODO."""

    heading: str
    time_stamps: list
    scheduled: OrgDate
    deadline: OrgDate
    properties: dict
    body: str
    args: list


class MaximalValid(OrgArguments):
    """Used to validate agenda item: maximal_valid.org."""

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


class MinimalValid(OrgArguments):
    """Used to validate agenda item: minimal_valid.org."""

    heading: str = 'Meeting'

    time_stamps: list = [OrgDate(datetime(2023, 1, 1, 1, 0),
                                 datetime(2023, 1, 1, 2, 0))]
    scheduled: OrgDate = OrgDate(None)
    deadline: OrgDate = OrgDate(None)
    properties: dict = {}
    body: str = "  <2023-01-01 Sun 01:00-02:00>"
    args: list = [heading, time_stamps, scheduled, deadline, properties, body]


class MultipleTimstampsValid(MaximalValid):
    """Used to validate agenda item: multile_timestamps.org."""

    time_stamps: list = [
        OrgDate(datetime(2023, 1, 1, 1, 0), datetime(2023, 1, 1, 2, 0)),
        OrgDate(datetime(2023, 1, 1, 3, 0), datetime(2023, 1, 1, 4, 0)),
        OrgDate(datetime(2023, 1, 1, 5, 0), datetime(2023, 1, 1, 6, 0))
    ]
    body: str = "  <2023-01-01 Sun 01:00-02:00>\n  <2023-01-01 Mon 03:00-04:00>\n  <2023-01-01 Tue 05:00-06:00>\n\n  Hello,\n\n  Lets have a meeting.\n\n  Regards,\n\n\n  Someone\n"
    args: list = [
        MaximalValid.heading,
        time_stamps,
        MaximalValid.scheduled,
        MaximalValid.deadline,
        MaximalValid.properties,
        body]
