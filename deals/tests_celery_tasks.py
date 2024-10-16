from django.test import TestCase
from django.test.utils import override_settings

from deals.tasks import send_email_to_assigned_user
from deals.tests_celery_tasks import DealModel


class TestCeleryTasks(DealModel, TestCase):
    @override_settings(
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
        CELERY_ALWAYS_EAGER=True,
        BROKER_BACKEND="memory",
    )
    def test_celery_tasks(self):
        task = send_email_to_assigned_user.apply(
            (
                [
                    self.user.id,
                    self.user1.id,
                ],
                self.deal.id,
            ),
        )
        self.assertEqual("SUCCESS", task.state)
