import datetime as dt

from django.test import TestCase
from django.utils import timezone

from gym.models import Member, Membership, MembershipType


class MembershipTests(TestCase):
    def setUp(self):
        self.member = Member.objects.create(
            first_name="Test",
            last_name="Member",
            email="member@example.com",
        )
        self.mtype = MembershipType.objects.create(
            name="Mensual",
            duration_days=30,
            price=10000,
            allows_classes=True,
        )

    def test_esta_vigente_true(self):
        today = timezone.localdate()
        membership = Membership.objects.create(
            member=self.member,
            type=self.mtype,
            start_date=today - dt.timedelta(days=1),
            end_date=today + dt.timedelta(days=28),
            status=Membership.Status.VIGENTE,
        )
        self.assertTrue(membership.esta_vigente())

    def test_esta_vigente_false_when_vencida(self):
        today = timezone.localdate()
        membership = Membership.objects.create(
            member=self.member,
            type=self.mtype,
            start_date=today - dt.timedelta(days=40),
            end_date=today - dt.timedelta(days=5),
            status=Membership.Status.VENCIDA,
        )
        self.assertFalse(membership.esta_vigente())

    def test_esta_vigente_false_outside_dates(self):
        today = timezone.localdate()
        membership = Membership.objects.create(
            member=self.member,
            type=self.mtype,
            start_date=today + dt.timedelta(days=1),
            end_date=today + dt.timedelta(days=30),
            status=Membership.Status.VIGENTE,
        )
        self.assertFalse(membership.esta_vigente())
