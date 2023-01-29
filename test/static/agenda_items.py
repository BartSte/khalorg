from datetime import datetime

from src.org_items import NvimOrgDate

_DESCRIPTION: str = (
    "  Hello,\n\n  Lets have a meeting.\n\n  Regards,\n\n\n  Someone"
)


class OrgArguments:
    """TODO."""

    heading: str
    time_stamps: list[NvimOrgDate]
    properties: dict = {}
    deadline: NvimOrgDate = NvimOrgDate(None)
    scheduled: NvimOrgDate = NvimOrgDate(None)

    _description: str = ''

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
            cls.get_body()]

    @classmethod
    def get_body(cls) -> str:
        date_in_body: list = [f'  {str(x)}\n' for x in cls.time_stamps]
        return ''.join(date_in_body) + cls._description


class MaximalValid(OrgArguments):
    """Used to validate agenda item: maximal_valid.org."""

    heading = 'Meeting'
    properties = {'ID': '123',
                        'CALENDAR': 'outlook',
                        "LOCATION": 'Somewhere',
                        "ORGANIZER": 'Someone (someone@outlook.com)',
                        "URL": 'www.test.com'}
    time_stamps = [NvimOrgDate((2023, 1, 1, 1, 0, 0), (2023, 1, 1, 2, 0, 0))]

    _description = _DESCRIPTION

    command_line_args = {
        'start': '2023-01-01 Sun 01:00',
        'end': '2023-01-01 Sun 02:00',
        'summary': 'Meeting',
        'description': (f'::   <2023-01-01 Sun 01:00-02:00>\n{_DESCRIPTION}'),
        '--location': 'Somewhere',
        '--url': 'www.test.com',
        }

    khal_new_args = ['-a Some_calendar',
                     '--location Somewhere',
                     '--url www.test.com',
                     '2023-01-01 Sun 01:00',
                     '2023-01-01 Sun 02:00',
                     '',
                     'Meeting',
                     f'::   <2023-01-01 Sun 01:00-02:00>\n{_DESCRIPTION}']


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

    @classmethod
    def get_body(cls) -> str:
        date_in_body: list = [f'  {str(x)}' for x in cls.time_stamps]
        return cls._description + '\n' + ''.join(date_in_body)
