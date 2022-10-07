from mock import patch
from freezegun import freeze_time

from django.test import TestCase

from ..models import Trip, CommentQty
from ..utils import wp_comments_qty as C
