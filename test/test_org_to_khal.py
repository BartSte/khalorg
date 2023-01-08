
from os.path import join
from test import static
from unittest import TestCase

from orgparse.node import OrgNode
from src.org_to_khal import parse_org_agenda_item

class TestParseOrgAgendaItem(TestCase):

    def setUp(self) -> None:
        self.org_agenda_item: str = join(
            static.__path__[0], 'valid.org')  # pyright:ignore
        return super().setUp()

    def test_valid_item(self):

        heading: str = "Meeting"
        body: str = "Hello,\n\nLets have a meeting\n\nRegards,\n\n\nSomeone"
        scheduled_start: datetime = datetime(2023, 1, 1, 12, 0)
        scheduled_end: datetime = datetime(2023, 1, 1, 13, 0)
        deadline_end: datetime = None
        properties: dict = {'ID': '123',
                            'CALENDAR': 'outlook',
                            "LOCATION": 'Somewhere',
                            "ORGANIZER":  'Someone (someone@outlook.com)'}

        # TODO: compare OrgAgendaItems for this test

#             ('heading', , node.heading),
#             ('scheduled.start', scheduled_start, node.scheduled.start),
#             ('scheduled.end', scheduled_end, node.scheduled.end),
#             ('deadline.end', deadline_end, node.deadline.end),
#             ('properties["ID"]', properties['ID'], node.properties['ID']),
#             ('properties["CALENDAR"]', properties['CALENDAR'], node.properties['CALENDAR']),  # noqa
#             ('properties["LOCATION"]', properties['LOCATION'], node.properties['LOCATION']),  # noqa
#             ('properties["ORGANIZER"]', properties['ORGANIZER'], node.properties['ORGANIZER']),  # noqa
#             ('body', body, node.body)

#         with open(self.org_agenda_item) as file_:
#             org_as_str: str = file_.read()
#             node: OrgNode = parse_org_agenda_item(org_as_str)

#         for (element, expected, actual) in compare:
#             self.assertEqual(expected, actual, msg=f'Failed at {element}')
