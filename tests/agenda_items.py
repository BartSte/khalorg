from datetime import datetime

from orgparse.date import OrgDate

_DESCRIPTION: str = (
    "Hello,\n\n  Lets have a meeting.\n\n  Regards,\n\n\n  Someone"
)


class OrgArguments:
    """
    Baseclass for representing the *.org files in the
    ./test/static/agenda_items/ directory, as python objects.
    """

    heading: str
    time_stamps: list[OrgDate]
    properties: dict = {}

    org_dates: dict

    description: str = ''

    @classmethod
    def get_args(cls) -> list:
        """

        Returns
        -------

        """
        return [
            cls.heading,
            cls.time_stamps,
            cls.properties,
            cls.description]


class Valid(OrgArguments):
    """Used to validate agenda item: valid.org."""

    heading = 'Meeting'
    properties = {
        "ATTENDEES": 'test@test.com, test2@test.com',
        "CALENDAR": 'outlook',
        "CATEGORIES": 'Something',
        "LOCATION": 'Somewhere',
        "ORGANIZER": 'Someone (someone@outlook.com)',
        "STATUS": 'CONFIRMED',
        'UID': '123',
        'UNTIL': '[2023-01-02 Mon 00:00]',
        "URL": 'www.test.com',
    }
    time_stamps = [OrgDate((2023, 1, 1, 1, 0, 0), (2023, 1, 1, 2, 0, 0))]
    org_dates = {
        '123': [
            OrgDate(
                (2023, 1, 1, 1, 0, 0), (2023, 1, 1, 2, 0, 0))]}

    description = _DESCRIPTION

    command_line_args = {
        'start': '2023-01-01 Sun 01:00',
        'end': '2023-01-01 Sun 02:00',
        'summary': 'Meeting',
        'description': (f':: {_DESCRIPTION}'),
        '--location': 'Somewhere',
        '--url': 'www.test.com',
        '--until': '2023-01-02 Mon',
    }

class Minimal(OrgArguments):
    """Used to validate agenda item: minimal.org."""

    heading: str = 'Meeting'
    time_stamps: list = [OrgDate(datetime(2023, 1, 1, 1, 0),
                                 datetime(2023, 1, 1, 2, 0))]

    org_dates = {
        '': [
            OrgDate(
                (2023, 1, 1, 1, 0, 0), (2023, 1, 1, 2, 0, 0))]}


class MultipleTimstampsValid(Valid):
    """Used to validate agenda item: multile_timestamps.org."""

    time_stamps: list = [
        OrgDate(datetime(2023, 1, 1, 1, 0), datetime(2023, 1, 1, 2, 0)),
        OrgDate(datetime(2023, 1, 2, 3, 0), datetime(2023, 1, 2, 4, 0)),
        OrgDate(datetime(2023, 1, 3, 5, 0), datetime(2023, 1, 3, 6, 0))
    ]


class NoHeading(Valid):
    """Used to validate agenda item: no_heading.org."""

    heading = ''


class NoTimestamp(Valid):
    """Used to validate agenda item: no_timestamp.org."""

    time_stamps = []


class NotFirstLevel(Valid):
    """Used to validate item: not_first_level.org."""

    pass


class BodyFirst(Valid):
    """Used to validate item: not_first_level.org."""

    pass


class Recurring(Valid):
    time_stamps = [
        OrgDate(
            start=(2023, 1, 1, 1, 0, 0),
            end=(2023, 1, 1, 2, 0, 0),
            repeater=('+', 1, 'w'))
    ]

    org_dates = {'123': [OrgDate((2023, 1, 1, 1, 0, 0),
                                 (2023, 1, 1, 2, 0, 0),
                                 True,
                                 ('+', 1, 'w'))]}
    command_line_args = {
        'start': '2023-01-01 Sun 01:00',
        'end': '2023-01-01 Sun 02:00',
        'summary': 'Meeting',
        'description': (f':: {_DESCRIPTION}'),
        '--location': 'Somewhere',
        '--url': 'www.test.com',
        '--repeat': 'weekly',
        '--until': '2023-01-02 Mon',
    }


class Duplicate(Valid):
    """Validates duplicates.org."""

    pass


class AllDay(Valid):
    """Used to validate agenda item: all_day.org."""

    time_stamps = [OrgDate((2023, 1, 1))]

    org_dates = {'123': [OrgDate((2023, 1, 1))]}

    description = _DESCRIPTION

    command_line_args = {
        'start': '2023-01-01 Sun',
        'end': '2023-01-01 Sun',
        'summary': 'Meeting',
        'description': (f':: {_DESCRIPTION}'),
        '--location': 'Somewhere',
        '--url': 'www.test.com',
        '--until': '2023-01-02 Mon',
    }

    khal_new_args = ['-a Some_calendar',
                     '--location Somewhere',
                     '--url www.test.com',
                     '--until 2023-01-02 Mon',
                     '2023-01-01 Sun',
                     '2023-01-01 Sun',
                     'Meeting',
                     f':: {_DESCRIPTION}\n']


class AllDayRecurring(Valid):
    time_stamps = [
        OrgDate(start=(2023, 1, 1), end=None, repeater=('+', 1, 'w'))
    ]

    org_dates = {
        '123': [
            OrgDate(
                (2023, 1, 1), (2023, 1, 1), True, ('+', 1, 'w'))]}

    command_line_args = {
        'start': '2023-01-01 Sun',
        'end': '2023-01-01 Sun',
        'summary': 'Meeting',
        'description': (f':: {_DESCRIPTION}'),
        '--location': 'Somewhere',
        '--url': 'www.test.com',
        '--repeat': 'weekly',
        '--until': '2023-01-02 Mon',
    }


class ShortTimestamp(Valid):
    """Validates othertimestamp.org."""

    pass
