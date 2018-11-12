from mock import patch

from django.test import TestCase

from ..models import Trip
from ..utils import wp_content as wp

class WpContentTest(TestCase):
    def setUp(self):
        self.trip = Trip.objects.create(
            title='Trip',
            start_date='2000-01-01',
            end_date='2000-06-01'
        )

        patcher_post = patch('project.maps.utils.wp_content.get_posts')
        self.mock_call = patcher_post.start()
        self.mock_call.return_value = [{'id': 101}, {'id': 102}]
        self.addCleanup(patcher_post.stop)


    def test_create_post_id_dictionary(self):
            dict = wp.create_post_id_dictionary(self.trip)

            self.assertDictEqual(dict, {101: 0, 102: 0})
