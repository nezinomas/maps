from django.test import TestCase
from mock import patch

from ..models import Trip

from ..utils import wp_comments_qty as qty


class WpCommentsQtyTest(TestCase):
    def setUp(self):
        self.trip = Trip.objects.create(
            title='Trip',
            start_date='2018-01-01',
            end_date='2018-02-01'
        )

    @patch(
        'project.maps.utils.wp_content.get_content',
        return_value=[{'post': 101}, {'post':102}, {'post':102}]
    )
    def test_count_comments_01(self, mock_call):
        q = qty._count_comments(self.trip)

        self.assertEqual(len(q), 2)
        self.assertDictEqual(q, {101: 1, 102: 2})
        self.assertEqual(mock_call.call_count, 1)

    @patch(
        'project.maps.utils.wp_comments_qty._get_wp_content',
        return_value=[]
    )
    def test_count_comments_02(self, mock_call):
        q = qty._count_comments(self.trip)

        self.assertEqual(len(q), 0)
        self.assertDictEqual(q, {})
        self.assertEqual(mock_call.call_count, 1)
