import datetime as dt

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from gym import services
from gym.models import Activity, ClassSession, Member, Membership, MembershipType, Trainer


class ClassCapacityTests(TestCase):
    def setUp(self):
        self.activity = Activity.objects.create(name="Funcional")
        self.trainer = Trainer.objects.create(
            first_name="Ana", last_name="Lopez", email="ana@example.com"
        )
        self.mtype = MembershipType.objects.create(
            name="Mensual", duration_days=30, price=10000, allows_classes=True
        )
        self.member1 = Member.objects.create(
            first_name="Uno", last_name="Socio", email="uno@example.com"
        )
        self.member2 = Member.objects.create(
            first_name="Dos", last_name="Socio", email="dos@example.com"
        )
        today = timezone.localdate()
        for member in (self.member1, self.member2):
            Membership.objects.create(
                member=member,
                type=self.mtype,
                start_date=today - dt.timedelta(days=1),
                end_date=today + dt.timedelta(days=28),
                status=Membership.Status.VIGENTE,
            )
        start = timezone.now() + dt.timedelta(days=1)
        self.class_session = ClassSession.objects.create(
            activity=self.activity,
            trainer=self.trainer,
            start=start,
            end=start + dt.timedelta(hours=1),
            capacity=1,
        )

    def test_no_puede_registrar_asistencia_si_clase_llena(self):
        services.registrar_asistencia_clase(self.member1, self.class_session)
        with self.assertRaises(ValidationError):
            services.registrar_asistencia_clase(self.member2, self.class_session)
