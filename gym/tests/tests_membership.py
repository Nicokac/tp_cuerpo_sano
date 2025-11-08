import datetime as dt
from django.test import TestCase
from django.utils import timezone
from gym.models import Member, MembershipType, Membership

class MembershipTests(TestCase):
    def setUp(self):
        self.member = Member.objects.create(
            first_name="nombretest",
            last_name="apellidotest",
            email="test@example.com",
        )
        self.mtype = MembershipType.objects.create(
            name="Mensual 30d", duration_days=30, price=10000.00, allows_classes=True
        )

    def test_esta_vigente_true(self):
        today = timezone.localdate()
        m = Membership.objects.create(
            member=self.member,
            type=self.mtype,
            start_date=today - dt.timedelta(days=1),
            end_date=today + dt.timedelta(days=29),
            status=Membership.Status.VIGENTE,
        )
        self.assertTrue(m.esta_vigente())

    def test_esta_vigente_false_when_vencida(self):
        today = timezone.localdate()
        m = Membership.objects.create(
            member=self.member,
            type=self.mtype,
            start_date=today - dt.timedelta(days=40),
            end_date=today - dt.timedelta(days=10),
            status=Membership.Status.VENCIDA,
        )
        self.assertFalse(m.esta_vigente())
