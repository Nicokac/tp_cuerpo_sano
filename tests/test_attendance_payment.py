import datetime as dt

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from gym import services
from gym.models import Attendance, Member, MembershipType, Payment


class AttendancePaymentTests(TestCase):
    def setUp(self):
        self.member = Member.objects.create(
            first_name="Socio",
            last_name="Prueba",
            email="socio@example.com",
        )
        self.mtype = MembershipType.objects.create(
            name="Mensual",
            duration_days=30,
            price=10000,
            allows_classes=True,
        )

    def test_bloquea_asistencia_sin_membresia(self):
        with self.assertRaises(ValidationError):
            services.registrar_asistencia_gym(self.member)

    def test_pago_aprobado_renueva_membresia(self):
        payment = Payment(
            member=self.member,
            membership_type=self.mtype,
            date=timezone.localdate(),
            amount=self.mtype.price,
            method=Payment.Method.EFECTIVO,
            status=Payment.Status.APROBADO,
        )
        payment.save()

        attendance = services.registrar_asistencia_gym(self.member)
        self.assertEqual(attendance.scope, Attendance.Scope.GYM)
        membership = services.membresia_vigente(self.member)
        self.assertIsNotNone(membership)
        self.assertTrue(membership.esta_vigente())
        expected_end = membership.start_date + dt.timedelta(days=self.mtype.duration_days - 1)
        self.assertEqual(membership.end_date, expected_end)
