from datetime import datetime

from src.org_items import NvimOrgDate

_DESCRIPTION: str = (
    "  Hello,\n\n  Lets have a meeting.\n\n  Regards,\n\n\n  Someone"
)


class OrgArguments:
    """
    Baseclass for representing the *.org files in the
    ./test/static/agenda_items/ directory, as python objects.
    """

    heading: str
    time_stamps: list[NvimOrgDate]
    properties: dict = {}
    deadline: NvimOrgDate = NvimOrgDate(None)
    scheduled: NvimOrgDate = NvimOrgDate(None)

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
            cls.scheduled,
            cls.deadline,
            cls.properties,
            cls.description]


class MaximalValid(OrgArguments):
    """Used to validate agenda item: maximal_valid.org."""

    heading = 'Meeting'
    properties = {'ID': '123',
                        'CALENDAR': 'outlook',
                        "LOCATION": 'Somewhere',
                        "ORGANIZER": 'Someone (someone@outlook.com)',
                        "ATTENDEES": 'test@test.com, test2@test.com',
                        "URL": 'www.test.com'}
    time_stamps = [NvimOrgDate((2023, 1, 1, 1, 0, 0), (2023, 1, 1, 2, 0, 0))]

    description = _DESCRIPTION

    command_line_args = {
        'start': '2023-01-01 Sun 01:00',
        'end': '2023-01-01 Sun 02:00',
        'summary': 'Meeting',
        'description': (f':: {_DESCRIPTION}'),
        '--location': 'Somewhere',
        '--url': 'www.test.com',
    }

    khal_new_args = ['-a Some_calendar',
                     '--location Somewhere',
                     '--url www.test.com',
                     '2023-01-01 Sun 01:00',
                     '2023-01-01 Sun 02:00',
                     'Meeting',
                     f':: {_DESCRIPTION}\n']


class MinimalValid(OrgArguments):
    """Used to validate agenda item: minimal_valid.org."""

    heading: str = 'Meeting'
    time_stamps: list = [NvimOrgDate(datetime(2023, 1, 1, 1, 0),
                                     datetime(2023, 1, 1, 2, 0))]


class MultipleTimstampsValid(MaximalValid):
    """Used to validate agenda item: multile_timestamps.org."""

    time_stamps: list = [
        NvimOrgDate(datetime(2023, 1, 1, 1, 0), datetime(2023, 1, 1, 2, 0)),
        NvimOrgDate(datetime(2023, 1, 2, 3, 0), datetime(2023, 1, 2, 4, 0)),
        NvimOrgDate(datetime(2023, 1, 3, 5, 0), datetime(2023, 1, 3, 6, 0))
    ]


class NoHeading(MaximalValid):
    """Used to validate agenda item: no_heading.org."""

    heading = ''


class NoTimestamp(MaximalValid):
    """Used to validate agenda item: no_timestamp.org."""

    time_stamps = []


class NotFirstLevel(MaximalValid):
    """Used to validate item: not_first_level.org."""

    pass


class BodyFirst(MaximalValid):
    """Used to validate item: not_first_level.org."""

    description = _DESCRIPTION + '\n  '


class Recurring(MaximalValid):
    time_stamps = [
        NvimOrgDate(
            start=(2023, 1, 1, 1, 0, 0),
            end=(2023, 1, 1, 2, 0, 0),
            repeater=('+', 1, 'w'))
    ]

    command_line_args = {
        'start': '2023-01-01 Sun 01:00',
        'end': '2023-01-01 Sun 02:00',
        'summary': 'Meeting',
        'description': (f':: {_DESCRIPTION}'),
        '--location': 'Somewhere',
        '--url': 'www.test.com',
        '--repeat': 'weekly'
    }


class Duplicate(MaximalValid):
    """Validates duplicates.org."""

    pass

class AllDay(MaximalValid):
    """Used to validate agenda item: all_day.org."""

    time_stamps = [NvimOrgDate((2023, 1, 1))]

    description = _DESCRIPTION

    command_line_args = {
        'start': '2023-01-01 Sun',
        'end': '2023-01-01 Sun',
        'summary': 'Meeting',
        'description': (f':: {_DESCRIPTION}'),
        '--location': 'Somewhere',
        '--url': 'www.test.com',
    }

    khal_new_args = ['-a Some_calendar',
                     '--location Somewhere',
                     '--url www.test.com',
                     '2023-01-01 Sun',
                     '2023-01-01 Sun',
                     'Meeting',
                     f':: {_DESCRIPTION}\n']

class ShortTimestamp(MaximalValid):
    """Validates othertimestamp.org."""

    pass
