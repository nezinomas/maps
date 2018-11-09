from mock import patch
from freezegun import freeze_time

from django.test import TestCase

from ..models import Trip, CommentQty
from ..utils import wp_comments_qty as qty


class WpCommentsQtyTest(TestCase):
    def setUp(self):
        self.trip = Trip.objects.create(
            title='Trip',
            start_date='2000-01-01',
            end_date='2000-06-01'
        )

        patcher = patch('project.maps.utils.wp_content.get_content')
        self.mock_call = patcher.start()
        self.mock_call.return_value = [{'post': 101}, {'post': 102}, {'post': 102}]
        self.addCleanup(patcher.stop)


    def test_count_comments_01(self):
        q = qty._count_comments(self.trip)

        self.assertEqual(len(q), 2)
        self.assertDictEqual(q, {101: 1, 102: 2})
        self.assertEqual(self.mock_call.call_count, 1)


    @patch(
        'project.maps.utils.wp_comments_qty._get_wp_content',
        return_value=[]
    )
    def test_count_comments_02(self, mock_call):
        q = qty._count_comments(self.trip)

        self.assertEqual(len(q), 0)
        self.assertDictEqual(q, {})
        self.assertEqual(mock_call.call_count, 1)


    def test_push_post_comment_qty(self):
        qty.push_post_comment_qty(self.trip)

        q = CommentQty.objects.all()

        self.assertEqual(len(q), 2)
        self.assertQuerysetEqual(q, ["<CommentQty: 101>", "<CommentQty: 102>"], ordered=False)
        self.assertEqual(self.mock_call.call_count, 1)


    @freeze_time("2000-06-01")
    def test_push_all_comment_qty_01(self):
        qty.push_all_comment_qty()

        q = CommentQty.objects.all()

        self.assertEqual(len(q), 0)


    @freeze_time("2000-03-01")
    def test_push_all_comment_qty_02(self):
        qty.push_all_comment_qty()

        q = CommentQty.objects.all()

        self.assertEqual(len(q), 2)
        self.assertQuerysetEqual(q, ["<CommentQty: 101>", "<CommentQty: 102>"], ordered=False)
